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
    cli = a109.AfterCli()
    monkeypatch.setattr(readers.Reader, "available", lambda self: True)
    original = readers.Reader.__init__

    def init(self, config, run_dir, runner=None, calls=None, _cache=None):
        original(self, config, run_dir, runner=cli)
    monkeypatch.setattr(readers.Reader, "__init__", init)
    monkeypatch.setattr(readers, "routing_version", lambda run_dir: "13")
    monkeypatch.setattr(readers, "spoken_guidelines", lambda bundle, cloud=None: q078.GUIDE)
    return SimpleNamespace(cli=cli, scores=tmp_path / "scores", out=tmp_path / "run")


def test_the_reader_files_name_the_dimension_placeholder_where_it_goes():
    for audience, parts in (("founder", ("screen", "after")), ("respondent", ("screen",))):
        for part in parts:
            text = readers.template(audience, part)
            assert text.count("{{dimension}}") == 1, (audience, part)
            assert text.index("{{persona}}") < text.index("{{dimension}}") < text.index("{{screen}}")
    assert "{{dimension}}" not in readers.template("founder", "after-insights")
    assert "{{dimension}}" not in readers.template("founder", "flow")
    assert not re.search(r"\{\{dimension\}\}", readers.template("respondent", "flow"))
