"""The question-quality readers (spec 078): the rubric file, the readers' prompts, the score file, the table, the
baseline, the refusals and the `read` mark kind -- with no model, no stack and no network.

Every reader call here goes to a fake runner standing where `subprocess.run` would be; the fixtures are a hand-sized
bundle and entry (`tests/fixtures/quality/bundle`, `entries/99-fixture.*`) and four score files over two entries and
two rubric versions (`tests/fixtures/quality/scores/`): `aa-alpha` has two files (the trend), `bb-beta` one at rubric
version 3 and one at version 2 -- set aside by the table, and refused when anything asks to average it with the rest.
Spec 081 moved every fixture to rubric version 2 (R6 2 on every respondent screen, the persona and guidelines header),
and spec 109 to version 3 (its §B screens are `tests/fixtures/quality/after-screens.json`'s, merged in by its tests);
the runner reads the guidelines from `tests/fixtures/quality/keel-cloud/` here, never the sibling checkout.
"""

from __future__ import annotations

import json
import re
import shutil
from pathlib import Path
from types import SimpleNamespace

import pytest

from instructions import judge as judge_mod
from instructions import marks as marks_mod
from quality import readers, rubric, table

REPO = Path(__file__).resolve().parent.parent
FX = Path(__file__).parent / "fixtures" / "quality"
BUNDLE = FX / "bundle"
ENTRIES = FX / "entries"
SCORES = FX / "scores"
DESIGN = REPO.parent / "keel-cloud-docs" / "canon" / "designs" / "question-quality-rubric-2026-10-28.md"

SCREEN_ANSWER = {"r1": 2, "why1": "fits", "r2": 1, "why2": "a second read", "r3": 2, "why3": "my life",
                 "r4": 2, "why4": "all four", "r5": 2, "why5": "kept", "instead": ""}
#: Spec 081 FR-4: the respondent-reader's answer carries R6 on every screen.
SPOKEN_ANSWER = {**SCREEN_ANSWER, "r6": 2, "why6": "says well"}
#: Spec 081 FR-4: the guidelines the runner pastes, from a fixture checkout (§2, §3, §5 of six sections).
FIXTURE_CLOUD = FX / "keel-cloud"
GUIDE = readers.spoken_guidelines({"stack": {}}, FIXTURE_CLOUD)


# ------------------------------------------------------------------------------------------------ fakes

class FakeCli:
    """Stands where `subprocess.run` is: answers the probe, a screen, a whole flow or a grouping, and records argv."""

    def __init__(self, *, screen=None, probe="ready", error=False):
        self.screen = SCREEN_ANSWER if screen is None else screen
        self.probe, self.error, self.seen = probe, error, []

    def __call__(self, argv, *, input, capture_output, text, timeout, env, cwd):    # noqa: A002 - run's own name
        self.seen.append({"argv": argv, "input": input, "env": env, "cwd": cwd})
        if "Reply with the one word" in input:
            result = self.probe
        elif "## The grouping to score" in input:
            result = json.dumps({"g1": 2, "why_g1": "plain", "g2": 2, "why_g2": "no junk answer on the line"})
        elif "## The whole" in input:
            result = json.dumps({"order": 2, "order_why": "fine", "asked_twice": "", "missing": ""})
        else:
            answer = self.screen
            if isinstance(answer, dict) and "## R6, said aloud" in input and "r6" not in answer:
                answer = {**answer, "r6": 2, "why6": "says well"}           # the respondent-reader's R6
            result = answer if isinstance(answer, str) else json.dumps(answer)
        body = {"type": "result", "is_error": self.error, "result": result, "total_cost_usd": 0.01,
                "modelUsage": {"claude-opus-5-5": {}}}
        return SimpleNamespace(stdout=json.dumps(body) + "\n", stderr="", returncode=0)


@pytest.fixture
def wired(monkeypatch, tmp_path):
    """The runner pointed at the fixture entry, a temporary scores dir, and a fake CLI on PATH."""
    monkeypatch.setattr(readers, "entries_dir", lambda: ENTRIES)
    cli = FakeCli()
    monkeypatch.setattr(readers.Reader, "available", lambda self: True)
    original = readers.Reader.__init__

    def init(self, config, run_dir, runner=None, calls=None, _cache=None):
        original(self, config, run_dir, runner=cli)
    monkeypatch.setattr(readers.Reader, "__init__", init)
    monkeypatch.setattr(readers, "routing_version", lambda run_dir: "13")
    monkeypatch.setattr(readers, "spoken_guidelines", lambda bundle, cloud=None: GUIDE)
    return SimpleNamespace(cli=cli, scores=tmp_path / "scores", out=tmp_path / "run")


def _run(w, *extra):
    return readers.run(["--run", str(BUNDLE), "--out", str(w.out), "--scores-dir", str(w.scores), *extra])


# --------------------------------------------------------------------------------------- FR-1 the rubric

def test_the_rubric_file_says_its_version_and_the_constant_agrees():
    assert rubric.RUBRIC_VERSION == 3 == rubric.file_version()           # spec 109 (was 2, spec 081)
    assert rubric.RETIRED == {1: rubric.RETIRED[1]} and "R6" in rubric.RETIRED[1]


def test_the_rubric_parses_into_six_criteria_with_their_anchors_as_the_design_has_them():
    """Spec 081: R1-R5 off the shared table, R6 off its own part; every anchor word for word in the design of record
    as amended 2026-10-28 (R2 plain to this person, R6 said aloud)."""
    rows = rubric.criteria()
    assert [r["id"] for r in rows] == ["r1", "r2", "r3", "r4", "r5", "r6"]
    assert [r["name"] for r in rows] == ["Fits here", "Plain to this person", "About their life", "The options",
                                         "The founder's words, kept", "Said aloud"]
    assert (rows[1]["2"], rows[1]["1"], rows[1]["0"]) == (
        "yes, in their own words", "needs a second read, or one word they would not use",
        "confusing, double-barrelled, or words of another trade")
    assert rows[5]["0"] == ("cannot be said: a parenthesis, a slash, an abbreviation only the eye reads, two questions "
                            "in one breath")
    assert rows[0]["0"] == "out of place, or asks what was already answered"
    assert rows[3]["0"] == "an option is nonsense, two mean the same, or the true answer is missing"
    assert rows[4]["0"] == "wrong, or leaks"
    if DESIGN.is_file():                                     # the design of record, read only, beside the worktree
        design = DESIGN.read_text(encoding="utf-8")
        for row in rows:
            for anchor in ("2", "1", "0"):
                assert row[anchor] in design, (row["id"], anchor)


def test_section_g_parses_into_two_criteria():
    rows = rubric.g_criteria()
    assert [r["id"] for r in rows] == ["g1", "g2"]
    assert "group a person in this job would recognise" in rows[0]["question"]
    assert rows[1]["0"] == "a junk answer grouped as if it were about this"


def test_the_prompt_part_carries_the_criteria_and_the_instead_line_but_not_the_weak_rule():
    part, spoken = rubric.prompt_rubric(), rubric.prompt_spoken()
    assert all(f"| R{i} |" in part for i in range(1, 6)) and "instead" in part
    assert "| R6 |" not in part and "| R6 |" in spoken, "R6 is the respondent-reader's part alone"
    assert "never the general public" in part, "spec 081 FR-2: the yardstick is this person, both readers"
    for text in (part, spoken):
        assert "weak" not in text.lower() and "score_pct" not in text, "the reader scores; code judges weak"


def test_a_rubric_without_its_markers_is_refused():
    with pytest.raises(rubric.RubricError):
        rubric.prompt_rubric("no markers here")


def test_the_two_booleans_are_codes_never_the_readers():
    meta = {"n": 1, "screen": "x", "audience": "founder", "link": None, "dimension": None, "kind": "q"}
    score = rubric.screen_score(meta, {**SCREEN_ANSWER, "r1": 0, "r4": 0})
    assert score["out_of_place"] and score["looks_stupid"]
    score = rubric.screen_score(meta, {**SCREEN_ANSWER, "r2": 0})
    assert not score["out_of_place"] and score["looks_stupid"]
    assert list(score) == list(rubric.SCORE_KEYS)
    said = rubric.screen_score({**meta, "audience": "respondent"}, {**SPOKEN_ANSWER, "r6": 0})
    assert said["looks_stupid"] and not said["out_of_place"], "spec 081 FR-4: R6 = 0 looks stupid"


def test_an_answer_is_read_from_a_fence_and_held_to_zero_one_two():
    fenced = "Here it is:\n```json\n" + json.dumps(SCREEN_ANSWER) + "\n```"
    assert rubric.parse_answer(fenced, has_options=True, audience="founder")["r2"] == 1
    with pytest.raises(rubric.RubricError):
        rubric.parse_answer(json.dumps({**SCREEN_ANSWER, "r3": 3}), has_options=True, audience="founder")
    with pytest.raises(rubric.RubricError):
        rubric.parse_answer("no object at all", has_options=True, audience="founder")


def test_r4_is_null_only_where_nothing_is_offered():
    assert rubric.parse_answer(json.dumps({**SCREEN_ANSWER, "r4": None}), has_options=False,
                               audience="founder")["r4"] is None
    with pytest.raises(rubric.RubricError):
        rubric.parse_answer(json.dumps({**SCREEN_ANSWER, "r4": None}), has_options=True, audience="founder")


def test_score_pct_is_the_sum_over_two_times_the_count_and_insights_fold_in():
    scores = [{"audience": "respondent", "r1": 2, "r2": 2, "r3": 1, "r4": None, "r5": 0},
              {"audience": "founder", "r1": 2, "r2": 2, "r3": 2, "r4": 2, "r5": 2}]
    alone = rubric.summary(scores)
    assert alone["score_pct"] == round(100 * 15 / 18, 1) and alone["flagged"] == 1 and alone["flagged_pct"] == 50.0
    both = rubric.summaries(scores, [{"g1": 2, "g2": 0}])
    assert both["respondent"]["score_pct"] == round(100 * (5 + 2) / (2 * 6), 1)
    assert both["respondent"]["insights_pct"] == 50.0 and "insights_pct" not in both["founder"]
    assert both["overall"]["score_pct"] == round(100 * (15 + 2) / (2 * 11), 1)


def test_two_rubric_versions_are_never_averaged():
    files = [rubric.load_file(p) for p in sorted(SCORES.glob("bb-beta/*.json"))]
    assert {f["rubric_version"] for f in files} == {2, 3}
    with pytest.raises(rubric.RubricMismatch):
        rubric.aggregate(files)
    with pytest.raises(rubric.RubricMismatch):
        table.rows({f"{f['entry']}{i}": f for i, f in enumerate(files)})


# ------------------------------------------------------------------------------- FR-2 / FR-3 the readers

def test_the_argv_is_the_judges_plus_the_pinned_model_and_effort():
    cfg = readers.load_reader_config()
    assert cfg["model"] == "claude-opus-5-5" and cfg["effort"] == "medium" and cfg["vendor"] == "anthropic"
    assert readers.reader_argv(cfg) == [*judge_mod._ARGV, "--model", "claude-opus-5-5", "--effort", "medium"]


def test_every_prompt_carries_the_rubric_from_the_file_and_no_placeholder():
    _, bundle = readers.load_bundle(BUNDLE)
    entry = readers.load_entry(bundle, ENTRIES)
    work = readers.plan(bundle, entry, guidelines=GUIDE)
    part, part_g = rubric.prompt_rubric(), rubric.prompt_insights()
    assert work["screens"] and all(part in p for _, p in work["screens"])
    assert work["insights"] and all(part_g in p for _, p in work["insights"])
    for prompt in [p for _, p in work["screens"]] + [p for *_, p in work["flows"]] + [p for _, p in work["insights"]]:
        assert "{{" not in prompt


def test_the_founder_reader_is_handed_the_sources_whole_and_the_earlier_screens_compact():
    _, bundle = readers.load_bundle(BUNDLE)
    entry = readers.load_entry(bundle, ENTRIES)
    founder = [(s, p) for s, p in readers.plan(bundle, entry, guidelines=GUIDE)["screens"] if s.audience == "founder"]
    screen, prompt = founder[2]
    assert screen.screen == "q-problem.prevalence" and screen.kind == "q" and screen.dimension == "problem.prevalence"
    assert entry["sources"].strip() in prompt
    earlier = prompt.split("## The screens you have already been through, in order", 1)[1].split("## The screen", 1)[0]
    assert "1. [NAME IT] What should we call this project?" in earlier
    assert "Night porters" not in earlier.split("2.", 1)[1], "the earlier screens are kicker and question only"
    assert "Fewer than 2 in 10" in prompt.split("## The screen to score", 1)[1], "the scored screen goes in full"


def test_the_respondent_reader_is_the_person_the_walk_took_on_each_link():
    _, bundle = readers.load_bundle(BUNDLE)
    entry = readers.load_entry(bundle, ENTRIES)
    primary = readers.persona(entry, bundle, "PRIMARY")
    assert "Your name is Ada Lindqvist." in primary and "Saturday night shift" in primary
    assert "Night porters" in primary and "window: the last 7 days" in primary
    commercial = readers.persona(entry, bundle, "COMMERCIAL_B2B")
    assert "Clara Mendes" in commercial and "Hotel manager" in commercial and "owns the budget" in commercial


def test_the_screener_is_its_own_screen_and_the_price_carries_its_plan():
    _, bundle = readers.load_bundle(BUNDLE)
    links = readers.respondent_screens(bundle)
    assert [s.kind for s in links["PRIMARY"]] == ["screener", "gate", "item", "reveal"]
    assert "Said aloud by the AI interviewer (the served spoken form)" in links["PRIMARY"][1].full
    price = next(s for s in links["COMMERCIAL_B2B"] if s.dimension == "commercial.price")
    assert "up front, per hotel?" in price.full and "Then, on the next screen" in price.full


def test_insight_lines_are_the_lines_with_two_answers_on_the_link_they_were_asked_on():
    _, bundle = readers.load_bundle(BUNDLE)
    lines = readers.insight_lines(bundle)
    assert [(l["dimension"], l["link"]) for l in lines] == [("problem.importance", "PRIMARY")], \
        "Price has one answer: no grouping to read"
    rendered = readers.render_line(lines[0])
    assert 'Group "Noise at night"' in rendered and "Every answer on it" in rendered
    still = {**bundle, "themes_settled": {"grouping": ["problem.importance"]}}
    assert readers.insight_lines(still) == [], "a line still grouping is not read"


# ------------------------------------------------------------------------------- FR-4 the score file

def test_a_run_writes_one_score_file_named_by_scope_and_it_round_trips(wired, capsys):
    assert _run(wired) == 0
    files = list(wired.scores.glob("99-fixture/*.json"))
    assert len(files) == 1
    name = files[0].name
    assert re.fullmatch(r"\d{8}-PROBLEM-r3-abcdef1-v13-claude-opus-5-5\.json", name), name
    obj = rubric.load_file(files[0])
    assert obj["entry"] == "99-fixture" and obj["scope"] == "PROBLEM" and obj["rubric_version"] == 3
    assert obj["cloud_sha"] == "abcdef12" and obj["web_sha"] == "1234567" and obj["routing_version"] == "13"
    assert obj["reader"] == {"model": "claude-opus-5-5", "effort": "medium", "vendor": "anthropic",
                             "door": "claude CLI"}
    assert len(obj["screens"]) == 3 + 4 + 3 and not obj["unread"] and obj["read_fraction"] == 1.0
    assert obj["insights"] == [{"line": "Why other things come first", "dimension": "problem.importance",
                                "link": "PRIMARY", "g1": 2, "g2": 2,
                                "whys": {"g1": "plain", "g2": "no junk answer on the line"}}]
    assert obj["flow"]["founder"]["order"] == 2 and set(obj["flow"]["respondent"]) == {"PRIMARY", "COMMERCIAL_B2B"}
    assert obj["summary"]["respondent"]["insights_pct"] == 100.0
    assert obj["entry_yaml"]["matches_bundle"] is True
    assert str(files[0]) in capsys.readouterr().out, "the path is printed"
    # every prompt and answer recorded under the run folder, the probe first
    calls = sorted((wired.out / "calls").glob("*.prompt.txt"))
    assert calls[0].name == "001-probe.prompt.txt" and len(calls) == 1 + 10 + 3 + 1
    assert all(c.with_name(c.name.replace(".prompt.txt", ".answer.json")).is_file() for c in calls)


def test_the_cli_is_called_as_the_judge_calls_it_with_the_effort_knobs_stripped(wired, monkeypatch):
    monkeypatch.setenv("CLAUDE_CODE_EFFORT_LEVEL", "max")
    assert _run(wired, "--limit", "1") == 0
    for call in wired.cli.seen:
        assert call["argv"][:len(judge_mod._ARGV)] == judge_mod._ARGV
        assert call["argv"][-4:] == ["--model", "claude-opus-5-5", "--effort", "medium"]
        assert "CLAUDE_CODE_EFFORT_LEVEL" not in call["env"]
        assert call["cwd"] == str(wired.out)


def test_a_partial_run_writes_its_score_in_the_run_folder_and_never_under_scores(wired):
    assert _run(wired, "--limit", "1") == 0
    assert not wired.scores.exists() or not list(wired.scores.rglob("*.json"))
    obj = json.loads((wired.out / "score.json").read_text())
    assert obj["partial"] is True and [s["audience"] for s in obj["screens"]] == ["founder", "respondent"]
    assert obj["insights"] == [] and obj["insights_note"] == "partial run: no grouping read"
    assert len(wired.cli.seen) == 3, "the probe and two screens"


def test_only_picks_by_dimension_on_both_audiences(wired):
    assert _run(wired, "--limit", "1", "--only", "problem.prevalence") == 0
    obj = json.loads((wired.out / "score.json").read_text())
    assert [(s["audience"], s["screen"]) for s in obj["screens"]] == [("founder", "q-problem.prevalence"),
                                                                      ("respondent", "gate")]


def test_an_unreadable_answer_leaves_the_screen_unread_not_scored(wired):
    wired.cli.screen = "I would rather not say"
    assert _run(wired, "--limit", "1") == 0
    obj = json.loads((wired.out / "score.json").read_text())
    assert obj["screens"] == [] and len(obj["unread"]) == 2 and obj["read_fraction"] == 0.0


def test_a_bundle_with_no_grouping_records_it_and_is_not_penalised(wired, tmp_path, monkeypatch):
    bundle = tmp_path / "bundle"
    shutil.copytree(BUNDLE, bundle)
    data = json.loads((bundle / "backtest.json").read_text())
    data["brief"] = {"insights": []}
    (bundle / "backtest.json").write_text(json.dumps(data))
    assert readers.run(["--run", str(bundle), "--out", str(wired.out), "--scores-dir", str(wired.scores)]) == 0
    obj = rubric.load_file(next(wired.scores.glob("99-fixture/*.json")))
    assert obj["insights"] == [] and obj["insights_note"].startswith("no grouping to read")
    assert obj["summary"]["respondent"]["insights_pct"] is None
    assert obj["summary"]["respondent"]["score_pct"] == rubric.summary(
        [s for s in obj["screens"] if s["audience"] == "respondent"])["score_pct"]


# ---------------------------------------------------------------------------------------- the refusals

def test_no_run_is_refused(capsys):
    assert readers.run([]) == 2
    assert "no RUN" in capsys.readouterr().err


def test_a_bundle_without_backtest_json_is_refused(tmp_path, capsys):
    assert readers.run(["--run", str(tmp_path)]) == 2
    assert "has no backtest.json" in capsys.readouterr().err


def test_no_claude_binary_is_refused_before_any_screen_and_writes_no_score(monkeypatch, tmp_path, capsys):
    monkeypatch.setattr(readers, "entries_dir", lambda: ENTRIES)
    monkeypatch.setattr(readers.shutil, "which", lambda name: None)
    assert readers.run(["--run", str(BUNDLE), "--out", str(tmp_path / "run"),
                        "--scores-dir", str(tmp_path / "scores")]) == 2
    err = capsys.readouterr().err
    assert "`claude` binary is not on PATH" in err and "key" not in err.lower()
    assert not (tmp_path / "scores").exists()


def test_a_failed_probe_is_refused_and_writes_no_score(wired, capsys):
    wired.cli.error = True
    assert _run(wired) == 2
    assert "could not answer a one-word probe" in capsys.readouterr().err
    assert not wired.scores.exists() and len(wired.cli.seen) == 1


def test_the_dry_run_prints_every_prompt_calls_nothing_and_writes_no_score(wired, capsys):
    assert _run(wired, "--dry-run") == 0
    out = capsys.readouterr().out
    assert wired.cli.seen == [] and not wired.scores.exists()
    prompts = sorted((wired.out / "prompts").glob("*.prompt.txt"))
    assert len(prompts) == 10 + 3 + 1 and out.count("=" * 100) == 2 * len(prompts) + 4, "+ the two heads (081)"
    assert "no call made, no score written" in out


def test_the_runner_reads_no_key():
    source = (REPO / "quality" / "readers.py").read_text(encoding="utf-8")
    assert "API_KEY" not in source and "environ[" not in source


# --------------------------------------------------------------------------------------- FR-5 the table

def test_the_table_reads_the_latest_file_per_study_and_sets_the_other_version_aside():
    files = table.load_scores(SCORES)
    current, aside = table.split_by_version(files)
    assert [Path(f["_path"]).name for f in aside] == ["20261030-PROBLEM-r2-abcdef1-v13-claude-opus-5-5.json"]
    latest = table.latest_per_entry(current)
    assert list(latest) == ["aa-alpha · PROBLEM", "bb-beta · PROBLEM"]
    assert latest["aa-alpha · PROBLEM"]["cloud_sha"] == "bcdef12", "the newer of aa-alpha's two"


def test_the_rows_carry_the_scope_the_means_and_the_weak_rule():
    current, _ = table.split_by_version(table.load_scores(SCORES))
    rows = {table.row_key(r): r for r in table.rows(table.latest_per_entry(current))}
    importance = rows["PROBLEM · respondent · problem.importance · item"]
    assert importance["weak"] and importance["weak_on"] == ["r4"], "a 0 on R4 in two entries"
    assert importance["zero_entries"]["r4"] == ["aa-alpha", "bb-beta"]
    assert importance["fix"]["category"] == "registry row"
    prevalence = rows["PROBLEM · founder · problem.prevalence · q"]
    assert not prevalence["weak"] and prevalence["means"]["r3"] == 1.5, "1.5 is not under 1.5"
    insights = rows["PROBLEM · respondent · problem.importance · insights"]
    assert insights["means"] == {"g1": 1.0, "g2": 2.0} and insights["weak_on"] == ["g1"]


def test_the_table_head_gives_score_pct_per_audience_and_scope_against_the_bar(tmp_path):
    files = table.load_scores(SCORES)
    text = table.render(files)
    assert "**Overall score_pct 91.2%**" in text and "meets the bar of **90%**" in text
    assert "- scope PROBLEM: score_pct 91.2%" in text
    assert "- respondent: score_pct 89.6%, spoken_pct 100.0%, insights_pct 75.0%" in text, "spec 081 FR-5"
    assert "Set aside (another rubric version, never averaged)" in text
    assert "| **WEAK** | PROBLEM | respondent | problem.importance | item |" in text
    assert "## Insights" in text and "| **WEAK** | PROBLEM | problem.importance | insights |" in text
    trend = text.split("## The trend", 1)[1]
    assert "88.9 ↓" in trend and "2.00 =" in trend and "2.00 ↑" in trend
    assert table.main(["--scores-dir", str(SCORES), "--out", str(tmp_path / "TABLE.md")]) == 0
    assert (tmp_path / "TABLE.md").read_text(encoding="utf-8") == text


def test_a_partial_score_file_is_refused_by_the_table(tmp_path, capsys):
    shutil.copytree(SCORES, tmp_path / "scores")
    path = next((tmp_path / "scores").glob("aa-alpha/*.json"))
    obj = json.loads(path.read_text())
    path.write_text(json.dumps({**obj, "partial": True}))
    assert table.main(["--scores-dir", str(tmp_path / "scores"), "--out", str(tmp_path / "T.md")]) == 2
    assert "is a partial run" in capsys.readouterr().err


def test_an_empty_scores_dir_still_builds_a_table_naming_the_bar(tmp_path):
    assert "The bar is **90%**" in table.render([])


# ------------------------------------------------------------------------------------- FR-6 the baseline

def _scores_copy(tmp_path):
    root = tmp_path / "scores"
    shutil.copytree(SCORES, root)
    return root


def test_no_baseline_is_refused_by_name(tmp_path):
    with pytest.raises(table.TableRefused, match="no baseline is cut yet"):
        table.read_baseline(tmp_path / "BASELINE.md")


def test_a_baseline_cut_compares_same_with_itself_and_worse_when_a_row_turns_weak(tmp_path):
    root = _scores_copy(tmp_path)
    base = tmp_path / "BASELINE.md"
    table.cut_baseline(table.load_scores(root), None, path=base, archive_dir=tmp_path / "baselines",
                       today="2026-10-28")
    data = table.read_baseline(base)
    assert data["studies"] == ["aa-alpha · PROBLEM", "bb-beta · PROBLEM"] and data["rubric_version"] == 3
    current, _ = table.split_by_version(table.load_scores(root))
    assert table.compare(data, table.latest_per_entry(current))["verdict"] == "same"
    # a later file for bb-beta where the founder's prevalence screen falls to 0 twice over: worse
    newer = json.loads(next(root.glob("bb-beta/20261028-*.json")).read_text())
    for s in newer["screens"]:
        if s["audience"] == "founder":
            s.update(r2=0, r3=0)
    newer["scored_at"] = "2026-10-31T12:00:00+00:00"
    (root / "bb-beta" / "20261031-PROBLEM-r3-abcdef1-v13-claude-opus-5-5.json").write_text(json.dumps(newer))
    current, _ = table.split_by_version(table.load_scores(root))
    result = table.compare(data, table.latest_per_entry(current))
    assert result["verdict"] == "worse" and "PROBLEM · founder · problem.prevalence · q" in result["why"]


def test_a_baseline_compares_like_with_like_and_better_when_a_weak_row_mends(tmp_path):
    root = _scores_copy(tmp_path)
    base = tmp_path / "BASELINE.md"
    table.cut_baseline(table.load_scores(root), ["aa-alpha"], path=base, today="2026-10-28")
    data = table.read_baseline(base)
    assert data["studies"] == ["aa-alpha · PROBLEM"]
    newer = json.loads(next(root.glob("aa-alpha/20261029-*.json")).read_text())
    for s in newer["screens"]:
        s.update({c: 2 for c in rubric.CRITERIA if s[c] is not None})
    newer["insights"][0].update(g1=2)
    newer["scored_at"] = "2026-10-31T12:00:00+00:00"
    (root / "aa-alpha" / "20261031-PROBLEM-r3-bcdef12-v13-claude-opus-5-5.json").write_text(json.dumps(newer))
    current, _ = table.split_by_version(table.load_scores(root))
    result = table.compare(data, table.latest_per_entry(current))
    assert result["verdict"] == "better"
    assert all(d["row"].startswith("PROBLEM") for d in result["rows"])
    assert not any("bb-beta" in str(d) for d in result["rows"]), "bb-beta is not in the baseline: not compared"


def test_a_new_cut_keeps_the_old_baseline(tmp_path):
    base, archive = tmp_path / "BASELINE.md", tmp_path / "baselines"
    files = table.load_scores(SCORES)
    table.cut_baseline(files, None, path=base, archive_dir=archive, today="2026-10-28")
    table.cut_baseline(files, None, path=base, archive_dir=archive, today="2026-11-02")
    assert (archive / "2026-10-28.md").is_file() and '"cut": "2026-11-02"' in base.read_text()


def test_a_baseline_at_another_rubric_version_is_refused(tmp_path):
    base = tmp_path / "BASELINE.md"
    table.cut_baseline(table.load_scores(SCORES), None, path=base, today="2026-10-28")
    base.write_text(base.read_text().replace('"rubric_version": 3', '"rubric_version": 2'))
    with pytest.raises(table.TableRefused, match="never compared"):
        table.read_baseline(base)


# ------------------------------------------------------------------------------------ FR-7 the `read` mark

def test_read_is_reported_from_the_latest_score_file_and_not_measured_otherwise():
    got = marks_mod.read_rows(["aa-alpha", "bb-beta", "01-countly"], SCORES)
    assert got["aa-alpha"]["measured"] and got["aa-alpha"]["file"].startswith("20261029-PROBLEM")
    assert got["aa-alpha"]["flagged"] == 1 and got["aa-alpha"]["means"]["r4"] == 1.0
    assert got["aa-alpha"]["insights_pct"] == 75.0 and got["aa-alpha"]["scope"] == "PROBLEM"
    assert got["bb-beta"]["measured"] and got["bb-beta"]["file"].startswith("20261028-PROBLEM-r3")
    assert got["01-countly"] == {"measured": False, "why": "not measured: no score file for this entry"}


def test_read_names_a_score_file_at_another_rubric_version_as_not_measured(tmp_path):
    (tmp_path / "cc-gamma").mkdir()
    shutil.copy(next(SCORES.glob("bb-beta/*-r2-*.json")), tmp_path / "cc-gamma" / "x.json")
    assert marks_mod.read_rows(["cc-gamma"], tmp_path)["cc-gamma"] == {
        "measured": False, "why": "not measured: rubric version [2], not 3"}


# ---------------------------------------------------------------------------------- FR-8 nothing else moves

def test_no_gate_names_the_readers():
    makefile = (REPO / "Makefile").read_text(encoding="utf-8")
    for name in ("eval: venv", "eval-live: venv", "unit: venv", "sample: venv", "instruction-eval: venv"):
        body = makefile.split(f"\n{name}\n", 1)[1].split("\n\n", 1)[0]
        assert "read-screens" not in body and "quality.readers" not in body, name
    for path in (REPO / "matrix").rglob("*"):
        if path.is_file() and path.suffix in (".py", ".toml", ".yml", ".yaml"):
            assert "read-screens" not in path.read_text(encoding="utf-8"), path
    assert not list((REPO / "quality").rglob("test_*.py")), "no pytest run collects a reader"


def test_the_make_targets_refuse_without_a_run_and_pass_dry_limit_and_only():
    makefile = (REPO / "Makefile").read_text(encoding="utf-8")
    body = makefile.split("\nread-screens: venv\n", 1)[1].split("\n\n", 1)[0]
    assert "make read-screens refuses: no RUN" in body and "--dry-run" in body and "--limit" in body
    assert "--only" in body and "KEY" not in body
    assert "--baseline" in makefile.split("\nread-table: venv\n", 1)[1].split("\n\n", 1)[0]


def test_the_score_files_are_committed_and_the_run_folders_ignored():
    ignore = (REPO / ".gitignore").read_text(encoding="utf-8")
    assert "runs/" in ignore.splitlines() and "quality" not in ignore
