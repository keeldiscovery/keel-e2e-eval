"""Spec 131 -- the readers know the dimension: the card in every prompt with a dimension (FR-2), R7 (FR-3, FR-1c), the
weak rule and the table (FR-5), the adviser handed the card (FR-4) -- with no model, no stack and no network.

The bundle is spec 078's fixture (`tests/fixtures/quality/bundle`) with spec 109's screens after the answers merged in
(`tests/fixtures/quality/after-screens.json`) and one Current solution Check screen: the angel-group scale of
2026-11-03 (spec 203), five shortfalls with the line under the first.
"""

from __future__ import annotations

import json
import re
import shutil
from pathlib import Path
from types import SimpleNamespace

import pytest

from quality import cards, readers, rubric
from tests import test_after_answers_109 as a109
from tests import test_quality_078 as q078

FX = Path(__file__).parent / "fixtures" / "quality"
AFTER = FX / "after-screens.json"

#: The angel-group screening study's Check screen as staging drew it on 2026-11-03 (spec 203's rungs, rebuilt in full by
#: keel-cloud's `TheScaleHasAWorkingRungTest`): five shortfalls, the line under the first.
ANGEL_ROWS = ["Inconsistent evidence across the decks", "Unsupported claims reached the committee",
              "Evidence too weak to decide on", "Never enough evidence to decide", "The screening failed outright"]
ANGEL_CHECK = {"n": 5, "screen": "check-problem.current_solution_satisfaction",
               "kicker": "STEP 2 OF 5 · THE PROBLEM · CHECK", "question": "", "hint": "",
               "title": "How did screening startup decks before the committee meets go?", "options": [],
               "rows": ANGEL_ROWS, "chips": [], "answer": "saved as Keel drafted it",
               "keel read back": {"belief": "For most angel investors, screening startup decks before the committee "
                                            "meets still falls short.",
                                  "bar": "Holds if at least 2 in 3 land below 'Inconsistent evidence across the decks'."}}


def bundle_dict() -> dict:
    data = json.loads((q078.BUNDLE / "backtest.json").read_text(encoding="utf-8"))
    extra = json.loads(AFTER.read_text(encoding="utf-8"))
    data["founder_screens"] = data["founder_screens"] + [extra["check_screen"], ANGEL_CHECK]
    data["after_screens"] = extra["after_screens"]
    return data


def write_bundle(tmp_path) -> Path:
    run = tmp_path / "bundle"
    shutil.copytree(q078.BUNDLE, run)
    (run / "backtest.json").write_text(json.dumps(bundle_dict()), encoding="utf-8")
    return run


@pytest.fixture(scope="module")
def work() -> dict:
    data = bundle_dict()
    entry = readers.load_entry(data, q078.ENTRIES)
    return readers.plan(data, entry, guidelines=q078.GUIDE)


def _prompt(work: dict, label: str) -> str:
    return next(p for s, p in work["screens"] if s.label() == label)


# ------------------------------------------------------------------------------------- FR-2 the card in the prompt

def test_every_screen_with_a_dimension_is_sent_its_card_and_no_other(work):
    sent = {s.label(): s.card for s, _ in work["screens"]}
    assert sent == {
        "founder-01-name": None, "founder-02-problem-card": None,
        "founder-03-q-problem.prevalence": "problem.prevalence",
        "founder-04-check-problem.prevalence": "problem.prevalence",
        "founder-05-check-problem.current_solution_satisfaction": "problem.current_solution_satisfaction",
        "founder-after-01-stage": None, "founder-after-02-dimension-problem.prevalence": "problem.prevalence",
        "founder-after-03-dimension-problem.importance": "problem.importance", "founder-after-04-insights": None,
        "respondent-PRIMARY-01-screener": None, "respondent-PRIMARY-02-gate": "problem.prevalence",
        "respondent-PRIMARY-03-item-problem.importance": "problem.importance", "respondent-PRIMARY-04-reveal": None,
        "respondent-COMMERCIAL_B2B-01-idea": None,
        "respondent-COMMERCIAL_B2B-02-item-commercial.price": "commercial.price",
        "respondent-COMMERCIAL_B2B-03-follow_up": None}
    for screen, prompt in work["screens"]:
        if screen.card:
            assert prompt.count(readers.DIMENSION_HEADING) == 1 and cards.card(screen.card) in prompt, screen.label()
            others = [k for k in cards.keys() if k != screen.card]
            assert not any(f"<!-- card:{k}" in prompt or f"### {k}" in prompt for k in others)
            assert all(cards.card(k) not in prompt for k in others), screen.label()
        else:
            assert readers.DIMENSION_HEADING not in prompt and "**Registry:**" not in prompt, screen.label()
    assert list(work["cards"]) == ["problem.prevalence", "problem.importance",          # the registry's order
                                   "problem.current_solution_satisfaction", "commercial.price"]


@pytest.mark.parametrize("label, persona", [
    ("founder-05-check-problem.current_solution_satisfaction", "## Who you are -- read this before the screen"),
    ("respondent-PRIMARY-03-item-problem.importance", "## Who you are -- read this before the screen"),
    ("founder-after-03-dimension-problem.importance", "## Who you are -- read this before the screen")])
def test_the_card_sits_after_the_persona_and_before_the_screen(work, label, persona):
    prompt = _prompt(work, label)
    at = prompt.index(readers.DIMENSION_HEADING)
    assert prompt.index(persona) < at < prompt.index("## The screen to score")
    assert prompt.index("## Your task") < at < prompt.index("## The rubric")      # the rubric, or §B's
    # the whole card, from its heading to its last line, nothing above its first marker
    key = next(s.card for s, _ in work["screens"] if s.label() == label)
    body = cards.card(key)
    assert prompt[prompt.index(body):].startswith(body) and "**What a card is.**" not in prompt


def test_the_dry_run_prints_each_card_once_and_names_it_where_it_is_sent(work):
    shown = readers.named_in_place(_prompt(work, "founder-05-check-problem.current_solution_satisfaction"), work)
    assert readers.DIMENSION_HEADING in shown
    assert "[the problem.current_solution_satisfaction card, printed above]" in shown
    assert cards.card("problem.current_solution_satisfaction") not in shown


def test_a_run_records_which_card_each_screen_was_sent(q078_wired, tmp_path):
    w = q078_wired
    run = write_bundle(tmp_path)
    assert readers.run(["--run", str(run), "--out", str(w.out), "--scores-dir", str(w.scores)]) == 0
    obj = rubric.load_file(next(w.scores.glob("99-fixture/*.json")))
    sent = {(s["audience"], s["link"], s["screen"]): s["dimension_card"] for s in obj["screens"]}
    assert sent[("founder", None, "check-problem.current_solution_satisfaction")] == \
        "problem.current_solution_satisfaction"
    assert sent[("founder", None, "problem-card")] is None and sent[("founder", None, "stage")] is None
    assert sent[("founder", None, "dimension-problem.importance")] == "problem.importance"
    assert sent[("respondent", "PRIMARY", "gate")] == "problem.prevalence"
    assert sent[("respondent", "COMMERCIAL_B2B", "follow_up")] is None
    assert all(list(s)[:7] == ["n", "screen", "audience", "link", "dimension", "kind", "dimension_card"]
               for s in obj["screens"])


@pytest.fixture
def q078_wired(monkeypatch, tmp_path):
    """Spec 078's wired runner (a fake CLI, the fixture entry, a temporary scores dir)."""
    monkeypatch.setattr(readers, "entries_dir", lambda: q078.ENTRIES)
    wired = SimpleNamespace(cli=a109.AfterCli(), scores=tmp_path / "scores", out=tmp_path / "run")
    monkeypatch.setattr(readers.Reader, "available", lambda self: True)
    original = readers.Reader.__init__

    def init(self, config, run_dir, runner=None, calls=None, _cache=None):
        original(self, config, run_dir, runner=wired.cli)                # the test may hand in another reader
    monkeypatch.setattr(readers.Reader, "__init__", init)
    monkeypatch.setattr(readers, "routing_version", lambda run_dir: "13")
    monkeypatch.setattr(readers, "spoken_guidelines", lambda bundle, cloud=None: q078.GUIDE)
    return wired


def test_the_reader_files_name_the_dimension_placeholder_where_it_goes():
    for audience, parts in (("founder", ("screen", "after")), ("respondent", ("screen",))):
        for part in parts:
            text = readers.template(audience, part)
            assert text.count("{{dimension}}") == 1, (audience, part)
            assert text.index("{{persona}}") < text.index("{{dimension}}") < text.index("{{screen}}")
    assert "{{dimension}}" not in readers.template("founder", "after-insights")
    assert "{{dimension}}" not in readers.template("founder", "flow")
    assert not re.search(r"\{\{dimension\}\}", readers.template("respondent", "flow"))


# --------------------------------------------------------------------------------- FR-3 / FR-1c R7, version 5

def test_the_rubric_is_at_version_5_and_its_prompt_part_holds_r7_in_the_cards_order():
    assert rubric.RUBRIC_VERSION == 5 == rubric.file_version()
    assert 4 not in rubric.RETIRED and 3 not in rubric.RETIRED, "versions 3 and 4 are set aside, never refused"
    part = rubric.prompt_rubric()
    r7 = next(r for r in rubric.criteria() if r["id"] == "r7")
    assert r7["name"] == "Fits the dimension" and "| R7 |" in part
    question = r7["question"]
    order = [question.index(w) for w in ("**the measure**", "**the shape**", "**the balance**", "**the escape**")]
    assert order == sorted(order), "FR-1c: the card's questions, in order"
    assert "could the belief ever be supported by these options? could it ever be refuted?" in question
    assert (r7["2"], r7["1"]) == ("all met", "one rule bent")
    for broken in ("every option counts one way", "a scale with no working rung", "options that cannot answer the belief",
                   "a missing escape the card requires"):
        assert broken in r7["0"]
    assert "`null` on a screen you were sent none" in part and "*Open* is never a fault" in part
    five = rubric.rubric_text().split("## Versions", 1)[1].split("- **4**", 1)[0]
    assert "- **5** (spec 131" in five and "R7, fits the dimension" in five
    assert "Version-4 files are set aside, never compared and never refused" in five


def test_r7_is_required_where_a_card_was_sent_and_refused_where_none_was():
    answer = {**q078.SCREEN_ANSWER, "r7": 0, "why7": "five shortfalls, no working rung"}
    said = rubric.parse_answer(json.dumps(answer), has_options=True, audience="founder", has_card=True)
    assert said["r7"] == 0 and said["why7"] == "five shortfalls, no working rung"
    with pytest.raises(rubric.RubricError, match="r7 is missing"):
        rubric.parse_answer(json.dumps(q078.SCREEN_ANSWER), has_options=True, audience="founder", has_card=True)
    with pytest.raises(rubric.RubricError, match="r7 on a screen sent no dimension card"):
        rubric.parse_answer(json.dumps(answer), has_options=True, audience="founder", has_card=False)
    assert rubric.parse_answer(json.dumps({**q078.SPOKEN_ANSWER, "r7": None}), has_options=True,
                               audience="respondent")["r7"] is None
    meta = {"n": 5, "screen": "check-problem.current_solution_satisfaction", "audience": "founder", "link": None,
            "dimension": "problem.current_solution_satisfaction", "kind": "check",
            "dimension_card": "problem.current_solution_satisfaction"}
    score = rubric.screen_score(meta, said)
    assert list(score) == list(rubric.SCORE_KEYS) and score["r7"] == 0
    assert rubric.flagged(score), "a 0 on R7 flags the screen like any other"
    assert not score["out_of_place"] and not score["looks_stupid"], "R7 moved no boolean"


class CardReaderCli(a109.AfterCli):
    """A scripted reader: on a screen sent its dimension card, R7 by the card's rules (`scripted_r7` of the cards'
    test) over the rows the screen shows -- the line under the first, as the bar names it; 2 on every other card."""

    def __call__(self, argv, *, input, capture_output, text, timeout, env, cwd):    # noqa: A002
        from tests.test_dimension_cards_131 import scripted_r7                     # noqa: PLC0415
        if readers.DIMENSION_HEADING in input and "## The beliefs you checked on the way in" not in input:
            key = re.search(r"^### .+ · `([a-z_.]+)`$", input, re.M).group(1)
            screen = input.split("## The screen to score", 1)[1]
            rows = re.findall(r"^  - (.+)$", screen.split("Rows:", 1)[1], re.M) if "Rows:" in screen else []
            r7, why = 2, "fits the card"
            if key == "problem.current_solution_satisfaction" and rows:
                r7, why = scripted_r7(cards.card(key), {"options": rows, "line": 1, "escape": "Someone else did it"})
            self.screen = {**q078.SCREEN_ANSWER, "r7": r7, "why7": why}
        else:
            self.screen = q078.SCREEN_ANSWER
        return super().__call__(argv, input=input, capture_output=capture_output, text=text, timeout=timeout,
                                env=env, cwd=cwd)


def test_the_angel_group_check_screen_scores_r7_0_and_is_flagged(q078_wired, tmp_path):
    """FR-6: the Check screen with five shortfall rungs scores R7 0 under a scripted reader handed its card; R7 is null
    on every screen sent none; the file round-trips at version 5 and R7 folds into score_pct, fits_pct beside it."""
    q078_wired.cli = CardReaderCli()
    run = write_bundle(tmp_path)
    assert readers.run(["--run", str(run), "--out", str(q078_wired.out), "--scores-dir", str(q078_wired.scores)]) == 0
    path = next(q078_wired.scores.glob("99-fixture/*.json"))
    assert re.fullmatch(r"\d{8}-PROBLEM-r5-abcdef1-v13-claude-opus-5-5\.json", path.name)
    obj = rubric.load_file(path)
    assert obj["rubric_version"] == 5 and not obj["unread"]
    by = {(s["audience"], s["link"], s["screen"]): s for s in obj["screens"]}
    angel = by[("founder", None, "check-problem.current_solution_satisfaction")]
    assert angel["r7"] == 0 and rubric.flagged(angel) and "no rung where today's way works" in angel["why7"]
    assert by[("founder", None, "check-problem.prevalence")]["r7"] == 2
    assert by[("respondent", "PRIMARY", "item-problem.importance")]["r7"] == 2
    for s in obj["screens"]:
        if not rubric.is_after(s["kind"]):
            assert (s["r7"] is None) == (s["dimension_card"] is None), s["screen"]
    founder = obj["summary"]["founder"]
    assert founder["means"]["r7"] == round((2 + 2 + 0) / 3, 3) and founder["fits_pct"] == round(100 * 4 / 6, 1)
    assert obj["summary"]["respondent"]["fits_pct"] == 100.0
    assert obj["summary"]["overall"]["zeros"]["r7"] == 1


# ------------------------------------------------------------------------------- FR-5 the weak rule and the table

def _r7_files(tmp_path, zeros: dict[str, int]) -> Path:
    """Spec 078's two fixture studies at version 5, their founder q screen sent the Prevalence card and scored R7 as
    `zeros` says (entry -> R7)."""
    root = tmp_path / "scores"
    for entry in ("aa-alpha", "bb-beta"):
        src = sorted(q078.SCORES.glob(f"{entry}/*-r5-*.json"))[-1]
        obj = json.loads(src.read_text(encoding="utf-8"))
        for s in obj["screens"]:
            if s["kind"] == "q":
                s.update(dimension_card=s["dimension"], r7=zeros.get(entry, 2), why7="read against the card")
        (root / entry).mkdir(parents=True)
        (root / entry / src.name).write_text(json.dumps(obj), encoding="utf-8")
    return root


def test_r7_is_a_criterion_of_the_weak_rule_with_its_column_and_its_fix(tmp_path):
    from quality import table                                            # noqa: PLC0415
    files = table.load_scores(_r7_files(tmp_path, {"aa-alpha": 0, "bb-beta": 0}))
    rows = {table.row_key(r): r for r in table.rows(table.latest_per_entry(files))}
    q = rows["PROBLEM · founder · problem.prevalence · q"]
    assert q["weak"] and "r7" in q["weak_on"] and q["zero_entries"]["r7"] == ["aa-alpha", "bb-beta"]
    assert table.CRITERION_FIX["r7"] in q["fix"]["also"]
    other = rows["PROBLEM · respondent · problem.importance · item"]
    assert other["means"]["r7"] is None and "r7" not in other["weak_on"], "no card sent: no R7 mean, never weak on it"
    text = table.render(files)
    assert "| R5 | R6 | R7 | 0s |" in text and "| R4 | R5 | R6 | R7 |" in text
    assert "fits_pct 0.0%" in text and "Fix for R7 -- the registry row's option rule" in text
    one = table.load_scores(_r7_files(tmp_path / "one", {"aa-alpha": 1}))
    q = {table.row_key(r): r for r in table.rows(table.latest_per_entry(one))}["PROBLEM · founder · problem.prevalence · q"]
    assert q["means"]["r7"] == 1.5 and "r7" not in q["weak_on"], "1.5 is not under 1.5, and no 0"


def test_a_baseline_carries_r7_and_the_comparison_its_delta(tmp_path):
    from quality import table                                            # noqa: PLC0415
    base = tmp_path / "BASELINE.md"
    table.cut_baseline(table.load_scores(_r7_files(tmp_path, {})), None, path=base, today="2026-11-03")
    data = table.read_baseline(base)
    assert data["rubric_version"] == 5
    assert data["rows"]["PROBLEM · founder · problem.prevalence · q"]["means"]["r7"] == 2.0
    assert "| R6 / B6 | R7 | weak |" in base.read_text(encoding="utf-8")
    now = table.latest_per_entry(table.load_scores(_r7_files(tmp_path / "now", {"aa-alpha": 0, "bb-beta": 0})))
    result = table.compare(data, now)
    row = next(d for d in result["rows"] if d["row"] == "PROBLEM · founder · problem.prevalence · q")
    assert row["delta"]["r7"] == -2.0 and result["verdict"] == "worse"


def test_a_version_4_file_is_set_aside_never_refused(tmp_path):
    from quality import table                                            # noqa: PLC0415
    root = _r7_files(tmp_path, {})
    old = json.loads(next((root / "bb-beta").glob("*.json")).read_text(encoding="utf-8"))
    old.update(rubric_version=4, scored_at="2026-11-02T00:00:00+00:00")
    for s in old["screens"]:
        for key in ("dimension_card", "r7", "why7"):
            s.pop(key, None)
    (root / "bb-beta" / "20261102-PROBLEM-r4-abcdef1-v13-claude-opus-5-5.json").write_text(json.dumps(old))
    files = table.load_scores(root)
    current, aside = table.split_by_version(files)
    assert [Path(f["_path"]).name for f in aside] == ["20261102-PROBLEM-r4-abcdef1-v13-claude-opus-5-5.json"]
    assert len(current) == 2
    with pytest.raises(rubric.RubricMismatch):
        rubric.aggregate(files)


def test_the_cycle_records_head_carries_r7_where_a_card_was_sent(tmp_path):
    from quality import cycle                                            # noqa: PLC0415
    from quality import table                                            # noqa: PLC0415
    files = table.load_scores(_r7_files(tmp_path, {"aa-alpha": 0}))
    head = cycle._head_of(files)
    assert head["fits"] == {"fits_pct": 50.0, "founder": 50.0, "respondent": None, "zeros": 1}
    from tests import test_quality_cycle_079 as c079                    # noqa: PLC0415
    _, data = c079.compose_the_fixture()
    assert "fits" not in data["head"], "a cycle whose screens were sent no card is 126's to the byte"
    text = cycle.render_record({**data, "head": {**data["head"], "fits": head["fits"]}})
    assert ("  - R7, fits the dimension (spec 131): fits_pct 50.0% over the screens sent a dimension card (founder "
            "50.0%, respondent –); 1 scored 0") in text


# ------------------------------------------------------------------------------------- FR-4 the adviser's card

def test_the_adviser_is_handed_the_rows_card_and_the_rule_to_keep_to_it():
    from quality import cycle                                            # noqa: PLC0415
    from tests import test_quality_cycle_079 as c079                    # noqa: PLC0415
    files = cycle.cycle_files(cycle.load_record(c079.RECORD))
    row = cycle.weak_rows(files)[0]
    assert row["dimension"] == "problem.importance"
    prompt = cycle.adviser_prompt(row, files, cloud=c079.CLOUD, cfg=cycle.load_config(), sha="abcdef1")
    assert "## The dimension's card (what its options must be, for every study)" in prompt
    assert cards.card("problem.importance") in prompt
    assert all(cards.card(k) not in prompt for k in cards.keys() if k != "problem.importance")
    assert "## The fix keeps to the dimension's card" in prompt and '"fits_card": true | false' in prompt
    assert prompt.index("## The current text at that location") < prompt.index("## The dimension's card")
    bare = cycle.adviser_prompt({**row, "dimension": "-"}, files, cloud=c079.CLOUD, cfg=cycle.load_config(),
                                sha="abcdef1")
    assert cycle.NO_CARD in bare and "**Registry:**" not in bare


def test_a_proposal_that_contradicts_the_card_is_refused_as_a_special_case():
    from quality import cycle                                            # noqa: PLC0415
    base = {"new_text": "Five outcomes, each how it fell short.", "why": "w", "rung": "words", "persona_aware": True}
    with pytest.raises(rubric.RubricError, match="fits_card"):
        cycle.parse_advice(json.dumps(base), has_card=True)
    assert cycle.parse_advice(json.dumps(base))["fits_card"] is True, "a row with no card: an answer without it reads"
    kept = cycle.parse_advice(json.dumps({**base, "fits_card": True}), has_card=True)
    assert cycle.special_case(kept) is None
    broke = cycle.parse_advice(json.dumps({**base, "fits_card": False}), has_card=True)
    assert "contradicts the dimension's card" in cycle.special_case(broke) and "spec 131 FR-4" in cycle.special_case(broke)
    assert "persona_aware false" in cycle.special_case({**broke, "persona_aware": False}), "081's reason first"


def test_a_card_contradicting_proposal_is_recorded_by_row_and_never_written_as_one(monkeypatch, tmp_path, capsys):
    from quality import cycle                                            # noqa: PLC0415
    from tests import test_quality_cycle_079 as c079                    # noqa: PLC0415
    monkeypatch.setattr(cycle, "DECISIONS", tmp_path / "no-decisions.toml")     # 079's cycle, no decision on file
    answer = json.dumps({"new_text": "Think of your last night. Which of these was hardest?", "why": "One. Two. Three.",
                         "rung": "words", "persona_aware": True, "fits_card": False})
    code, out, _ = c079._advise(monkeypatch, tmp_path, answer)
    assert code == 0 and "REFUSED: a special case" in capsys.readouterr().out
    text = out.read_text(encoding="utf-8")
    section = text.split(f"## 1. {c079.WEAK_ROW}", 1)[1]
    assert "**Refused -- not a proposal** (spec 081 FR-6)" in section and "contradicts the dimension's card" in section
    assert "The proposed text:" not in section
    data = json.loads(text.split("<!-- advice:data -->", 1)[1].split("```json", 1)[1].split("```", 1)[0])
    assert data["proposals"][0]["card"] == "problem.importance" and data["proposals"][0]["fits_card"] is False
