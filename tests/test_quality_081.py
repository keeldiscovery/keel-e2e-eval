"""Rubric version 2 (spec 081): R2 plain to this person, the persona block handed before any screen, R6 said aloud on
every respondent screen against keel-cloud's spoken-question guidelines, `spoken_pct`, the version refusal, and the
adviser that never proposes a special case -- with no model, no stack and no network.

The bundle, the entry and the score fixtures are 078's and 079's (moved to version 2 by this spec); the guidelines are
read from `tests/fixtures/quality/keel-cloud/` (six sections, of which §2, §3 and §5 are pasted), or from a temporary
git checkout where the bundle's sha matters.
"""

from __future__ import annotations

import copy
import json
import subprocess
from pathlib import Path

import pytest

from quality import cycle, readers, rubric, table
from tests.test_quality_078 import BUNDLE, DESIGN, ENTRIES, GUIDE, SCORES, SCREEN_ANSWER, SPOKEN_ANSWER, _run
from tests.test_quality_078 import wired  # noqa: F401 - the fixture, shared
from tests.test_quality_cycle_079 import CLOUD, RECORD, WEAK_ROW, _advise
from tests.test_quality_cycle_079 import no_decisions  # noqa: F401 - the fixture: no decision on file (spec 087)

FIXTURE_CLOUD = Path(__file__).parent / "fixtures" / "quality" / "keel-cloud"
R6_ROW = "| R6 | **Said aloud.**"
YARDSTICK = "never the general public"


def _work(**over):
    _, bundle = readers.load_bundle(BUNDLE)
    entry = readers.load_entry(bundle, ENTRIES)
    entry["yaml"] = {**entry["yaml"], "market": {"country": "PT", "region": "Lisbon"}}
    return bundle, entry, readers.plan(bundle, entry, guidelines=GUIDE, **over)


# ------------------------------------------------------------------------------------------ FR-1 the version

def test_the_rubric_is_at_version_2_and_says_what_changed_and_why():
    assert rubric.RUBRIC_VERSION == 2 == rubric.file_version()
    versions = rubric.rubric_text().split("## Versions", 1)[1]
    two = versions.split("- **1**", 1)[0]
    assert "- **2** (spec 081" in two and "R2 is judged from inside the persona" in two
    assert "R6, said aloud" in two and "persona block is handed before any screen" in two
    assert "nothing is re-scored" in two and "refused by name" in two


def test_a_score_file_at_version_1_is_refused_by_name_and_the_table_names_its_path(tmp_path, capsys):
    obj = json.loads(next(SCORES.glob("aa-alpha/*.json")).read_text())
    old = {**obj, "rubric_version": 1}
    with pytest.raises(rubric.RubricError, match=r"old\.json is at rubric version 1, before spec 081"):
        rubric.validate_file(old, name="old.json")
    (tmp_path / "scores" / "aa-alpha").mkdir(parents=True)
    path = tmp_path / "scores" / "aa-alpha" / "20261028-PROBLEM-r1-abcdef1-v13-claude-opus-5-5.json"
    path.write_text(json.dumps(old))
    with pytest.raises(table.TableRefused, match="20261028-PROBLEM-r1-abcdef1"):
        table.load_scores(tmp_path / "scores")
    assert table.main(["--scores-dir", str(tmp_path / "scores"), "--out", str(tmp_path / "T.md")]) == 2
    assert "rubric version 1" in capsys.readouterr().err and not (tmp_path / "T.md").exists()


def test_a_file_at_another_unretired_version_is_still_set_aside_not_refused():
    files = table.load_scores(SCORES)
    _, aside = table.split_by_version(files)
    assert [f["rubric_version"] for f in aside] == [3]


def test_the_fixtures_are_at_version_2_with_r6_on_every_respondent_screen():
    paths = sorted(SCORES.glob("*/*.json")) + sorted((Path(__file__).parent / "fixtures" / "quality" / "cycle" /
                                                      "scores").glob("*/*.json"))
    current = [json.loads(p.read_text()) for p in paths if "-r2-" in p.name]
    assert len(current) == 7 and all(f["rubric_version"] == 2 for f in current)
    for f in current:
        assert set(f["persona"]) == {"founder", "respondent"} and f["spoken_guidelines"]["sections"] == ["2", "3", "5"]
        for s in f["screens"]:
            assert (s["r6"] is None) == (s["audience"] == "founder"), (f["entry"], s["screen"])


# --------------------------------------------------------------------------------------------- FR-2 R2

def test_r2s_anchors_are_the_designs_and_both_readers_carry_the_yardstick():
    r2 = next(r for r in rubric.criteria() if r["id"] == "r2")
    assert r2["name"] == "Plain to this person"
    assert (r2["2"], r2["1"], r2["0"]) == ("yes, in their own words",
                                           "needs a second read, or one word they would not use",
                                           "confusing, double-barrelled, or words of another trade")
    if DESIGN.is_file():
        design = DESIGN.read_text(encoding="utf-8")
        for row in rubric.criteria():
            for anchor in ("2", "1", "0"):
                assert row[anchor] in design, (row["id"], anchor)
    _, _, work = _work()
    for screen, prompt in work["screens"]:
        task = prompt.split("## Your task", 1)[1].split("## The rubric", 1)[0]
        assert YARDSTICK in task and "your trade, your place, your time of life" in task, screen.label()
    assert YARDSTICK in rubric.prompt_rubric()


# ------------------------------------------------------------------------------------- FR-3 the persona block

def test_every_prompt_opens_with_its_persona_block_once():
    _, _, work = _work()
    blocks = work["persona"]
    assert set(blocks["respondent"]) == {"PRIMARY", "COMMERCIAL_B2B"}
    prompts = ([(s.audience, s.link, p) for s, p in work["screens"]] + [(a, link, p) for a, link, p in work["flows"]]
               + [("respondent", line["link"], p) for line, p in work["insights"]])
    assert len(prompts) == 10 + 3 + 1
    for audience, link, prompt in prompts:
        block = blocks["founder"] if audience == "founder" else blocks["respondent"][link]
        assert prompt.startswith("## Who you are -- read this "), (audience, link)
        assert prompt.split("\n\n", 1)[1].startswith(block), "the block is the first thing after the heading"
        assert prompt.count(block) == 1 and prompt.count("## Who you are") == 1


def test_the_respondent_block_is_the_person_and_the_projects_what_where_when():
    _, _, work = _work()
    primary = work["persona"]["respondent"]["PRIMARY"]
    assert "Your name is Ada Lindqvist." in primary and "Night porters" in primary
    for line in ("  actor: night porter", "  actor_plural: night porters at small hotels",
                 "  job: keep the night desk running", "  circumstance: guests arrive after midnight",
                 "  segment: night porters at small hotels in Portugal", "  window: the last 7 days",
                 "  where: PT, Lisbon"):
        assert line in primary, line
    founder = work["persona"]["founder"]
    _, entry, _ = _work()
    assert entry["sources"].strip() in founder and "  where: PT, Lisbon" in founder
    assert "  window: the last 7 days" in founder


def test_the_score_file_records_the_persona_once_in_its_header(wired):  # noqa: F811
    assert _run(wired) == 0
    path = next(wired.scores.glob("99-fixture/*.json"))
    obj = rubric.load_file(path)
    keys = list(obj)
    assert keys.index("persona") < keys.index("screens") and keys.index("spoken_guidelines") < keys.index("screens")
    assert set(obj["persona"]["respondent"]) == {"PRIMARY", "COMMERCIAL_B2B"}
    assert "Your name is Ada Lindqvist." in obj["persona"]["respondent"]["PRIMARY"]
    assert not any("persona" in s for s in obj["screens"]), "once, not per screen"
    assert path.read_text().count("Your name is Ada Lindqvist.") == 1
    assert obj["spoken_guidelines"] == {k: GUIDE[k] for k in ("source", "sections", "sha256")}
    headless = {k: v for k, v in obj.items() if k != "persona"}
    with pytest.raises(rubric.RubricError, match="without \\['persona'\\]"):
        rubric.validate_file(headless)


# ------------------------------------------------------------------------------------------ FR-4 R6

def test_the_guidelines_are_sections_2_3_and_5_pasted_into_every_respondent_screen_prompt_alone():
    assert "FIXTURE-SECTION-2" in GUIDE["text"] and "FIXTURE-SECTION-3" in GUIDE["text"]
    assert "FIXTURE-SECTION-5" in GUIDE["text"]
    assert not any(f"FIXTURE-SECTION-{n}" in GUIDE["text"] for n in (1, 4, 6))
    _, _, work = _work()
    for screen, prompt in work["screens"]:
        said = screen.audience == "respondent"
        assert (R6_ROW in prompt) is said and (GUIDE["text"] in prompt) is said, screen.label()
        assert ('"r6": 0|1|2' in prompt) is said, screen.label()
    for *_, prompt in work["flows"]:
        assert R6_ROW not in prompt


def test_the_guidelines_are_read_at_the_bundles_sha_where_it_carries_them_else_from_the_checkout(tmp_path):
    cloud = tmp_path / "cloud"
    target = cloud / readers.GUIDELINES_REL
    target.parent.mkdir(parents=True)
    target.write_text((FIXTURE_CLOUD / readers.GUIDELINES_REL).read_text().replace("FIXTURE-SECTION-2",
                                                                                   "AT-THE-SHA"))
    quiet = {"capture_output": True, "check": True}
    subprocess.run(["git", "-C", str(cloud), "init", "-q"], **quiet)
    subprocess.run(["git", "-C", str(cloud), "add", "-A"], **quiet)
    subprocess.run(["git", "-C", str(cloud), "-c", "user.name=t", "-c", "user.email=t@t", "commit", "-qm", "c"], **quiet)
    sha = subprocess.run(["git", "-C", str(cloud), "rev-parse", "--short=8", "HEAD"], **quiet, text=True).stdout.strip()
    target.write_text(target.read_text().replace("AT-THE-SHA", "IN-THE-CHECKOUT"))       # the checkout moved on
    at_sha = readers.spoken_guidelines({"stack": {"keel-cloud": sha}}, cloud)
    assert "AT-THE-SHA" in at_sha["text"] and at_sha["source"] == f"keel-cloud {sha} (the bundle's)"
    elsewhere = readers.spoken_guidelines({"stack": {"keel-cloud": "0000000"}}, cloud)
    assert "IN-THE-CHECKOUT" in elsewhere["text"] and "does not carry it" in elsewhere["source"]
    target.write_text("# no sections\n")
    with pytest.raises(readers.Refused, match="no section 2"):
        readers.spoken_guidelines({"stack": {}}, cloud)


def test_every_respondent_screen_says_how_the_avatar_says_it():
    links = readers.respondent_screens(readers.load_bundle(BUNDLE)[1])
    gate = links["PRIMARY"][1]
    assert gate.said == "In the last 7 days, did a guest arrive after midnight on your shift? Yes or no."
    assert "(the served spoken form)" in gate.full
    for screen in [s for screens in links.values() for s in screens]:
        assert screen.said and "Said aloud by the AI interviewer" in screen.full, screen.label()
    item = next(s for s in links["PRIMARY"] if s.kind == "item")
    assert "the guidelines' §3 template filled from this screen" in item.full


def test_the_section_3_template():
    assert readers.spoken_template("Which of these came first?", ["A", "B", "C"], "None of these") == \
        "Which of these came first? I'll read 3 options. A; B; or C. Or say None of these."
    assert readers.spoken_template("Which two?", ["A", "B"], None, pick_two=True) == \
        "Which two? I'll read 2 options; pick two. A; or B."
    assert readers.spoken_template("In your own words, what came first?") == "In your own words, what came first?"


def test_r6_is_required_of_the_respondent_reader_and_refused_of_the_founder_reader():
    said = rubric.parse_answer(json.dumps(SPOKEN_ANSWER), has_options=True, audience="respondent")
    assert said["r6"] == 2 and said["why6"] == "says well"
    with pytest.raises(rubric.RubricError, match="r6 is missing"):
        rubric.parse_answer(json.dumps(SCREEN_ANSWER), has_options=True, audience="respondent")
    with pytest.raises(rubric.RubricError, match="r6 on a founder screen"):
        rubric.parse_answer(json.dumps(SPOKEN_ANSWER), has_options=True, audience="founder")
    with pytest.raises(rubric.RubricError):
        rubric.parse_answer(json.dumps({**SPOKEN_ANSWER, "r6": 3}), has_options=True, audience="respondent")
    assert rubric.parse_answer(json.dumps(SCREEN_ANSWER), has_options=True, audience="founder")["r6"] is None


def test_a_score_file_is_refused_without_r6_on_a_respondent_screen_or_with_one_on_a_founder_screen():
    obj = json.loads(next(SCORES.glob("aa-alpha/*.json")).read_text())
    rubric.validate_file(copy.deepcopy(obj))
    bare = copy.deepcopy(obj)
    next(s for s in bare["screens"] if s["audience"] == "respondent")["r6"] = None
    with pytest.raises(rubric.RubricError, match="has no R6"):
        rubric.validate_file(bare)
    stray = copy.deepcopy(obj)
    next(s for s in stray["screens"] if s["audience"] == "founder")["r6"] = 2
    with pytest.raises(rubric.RubricError, match="carries an R6"):
        rubric.validate_file(stray)


def test_r6_folds_into_score_pct_with_spoken_pct_beside_and_a_zero_looks_stupid():
    founder = {"audience": "founder", "r1": 2, "r2": 2, "r3": 2, "r4": 2, "r5": 2, "r6": None}
    stranger = {"audience": "respondent", "r1": 2, "r2": 2, "r3": 2, "r4": None, "r5": 2, "r6": 0}
    sums = rubric.summaries([founder, stranger])
    assert sums["respondent"]["score_pct"] == round(100 * 8 / 10, 1) and sums["respondent"]["spoken_pct"] == 0.0
    assert sums["founder"]["spoken_pct"] is None and sums["founder"]["means"]["r6"] is None
    assert sums["overall"]["score_pct"] == round(100 * 18 / 20, 1) and sums["overall"]["flagged"] == 1
    meta = {"n": 1, "screen": "x", "audience": "respondent", "link": "PRIMARY", "dimension": None, "kind": "item"}
    assert rubric.screen_score(meta, {**SPOKEN_ANSWER, "r6": 0})["looks_stupid"] is True


def test_a_run_reads_r6_on_every_respondent_screen(wired):  # noqa: F811
    assert _run(wired) == 0
    obj = rubric.load_file(next(wired.scores.glob("99-fixture/*.json")))
    for s in obj["screens"]:
        assert (s["r6"] == 2) if s["audience"] == "respondent" else (s["r6"] is None), s["screen"]
    assert obj["summary"]["respondent"]["spoken_pct"] == 100.0 and obj["summary"]["founder"]["spoken_pct"] is None


def test_the_dry_run_prints_each_persona_block_once_and_r6_in_every_respondent_prompt(wired, capsys):  # noqa: F811
    assert _run(wired, "--dry-run") == 0
    out = capsys.readouterr().out
    assert out.count("Your name is Ada Lindqvist.") == 1 and out.count("Your name is Clara Mendes.") == 1
    assert out.count("FIXTURE-SECTION-2") == 1, "the guidelines printed once, named in place"
    chunks = out.split("=" * 100)
    respondent = [chunks[i + 1] for i, c in enumerate(chunks) if "] respondent-" in c]
    assert len(respondent) == 7 and all(R6_ROW in c and "[the spoken-question guidelines" in c for c in respondent)
    founder = [chunks[i + 1] for i, c in enumerate(chunks) if "] founder-" in c]
    assert founder and all("[the founder's persona block, printed above]" in c and R6_ROW not in c for c in founder)
    saved = sorted((wired.out / "prompts").glob("[0-9][0-9][0-9]-respondent-*.prompt.txt"))
    assert saved and all("Your name is" in p.read_text() and "FIXTURE-SECTION-5" in p.read_text() for p in saved)


# -------------------------------------------------------------------------------------------- FR-5 the table

def _weak_on_r6(tmp_path):
    root = tmp_path / "scores"
    for entry in ("aa-alpha", "bb-beta"):
        src = next(SCORES.glob(f"{entry}/*-r2-*.json"))
        obj = json.loads(src.read_text())
        for s in obj["screens"]:
            if s["audience"] == "respondent" and s["kind"] == "reveal":
                s.update(r6=0, why6="a parenthesis that does not say well", looks_stupid=True)
        obj["summary"] = rubric.summaries(obj["screens"], obj.get("insights") or [])
        (root / entry).mkdir(parents=True, exist_ok=True)
        (root / entry / src.name).write_text(json.dumps(obj))
    return root


def test_r6_is_a_column_on_respondent_rows_and_a_weak_r6_names_where_it_is_fixed(tmp_path):
    files = table.load_scores(_weak_on_r6(tmp_path))
    rows = {table.row_key(r): r for r in table.rows(table.latest_per_entry(files))}
    reveal = rows["PROBLEM · respondent · - · reveal"]
    assert reveal["weak_on"] == ["r6"] and reveal["spoken_pct"] == 0.0
    assert reveal["fix"]["also"] == [table.CRITERION_FIX["r6"]]
    assert "the registry row's wording or the spoken transform" in table.CRITERION_FIX["r6"]
    assert "the instruction gains the trade's words" in table.CRITERION_FIX["r2"]
    founder = rows["PROBLEM · founder · problem.prevalence · q"]
    assert founder["means"]["r6"] is None and "also" not in founder["fix"]
    text = table.render(files)
    assert "| R5 | R6 | 0s |" in text and "spoken_pct 50.0%" in text
    assert "Fix for R6 -- the registry row's wording or the spoken transform" in text
    assert "| PROBLEM | founder | problem.prevalence | q | 2 | 2.00 | 2.00 | 1.50 | 2.00 | 2.00 | – |" in text


def test_the_committed_table_is_built_at_version_2():
    text = (Path(table.__file__).parent / "TABLE.md").read_text(encoding="utf-8")
    assert "at RUBRIC_VERSION 2." in text and "| R5 | R6 | 0s |" in text


# --------------------------------------------------------------------------------------- FR-6 the adviser

def test_the_adviser_prompt_carries_the_persona_aware_rule():
    files = cycle.cycle_files(cycle.load_record(RECORD))
    rows = cycle.weak_rows(files)
    prompt = cycle.adviser_prompt(rows[0], files, cloud=CLOUD, cfg=cycle.load_config(), sha="abcdef1")
    assert "## The fix is persona awareness, never a special case" in prompt
    assert "no *if the people are mariners, say" in prompt and '"persona_aware": true | false' in prompt


def test_persona_aware_is_required_and_a_special_case_is_refused_whatever_the_flag():
    base = {"new_text": "Think of that night. Which two of these would you most like made easier?", "why": "w",
            "rung": "words"}
    with pytest.raises(rubric.RubricError, match="persona_aware"):
        cycle.parse_advice(json.dumps(base))
    assert cycle.special_case(cycle.parse_advice(json.dumps({**base, "persona_aware": True}))) is None
    assert "persona_aware false" in cycle.special_case(cycle.parse_advice(json.dumps({**base, "persona_aware": False})))
    for text in ("If the people are mariners, say nautical miles; otherwise say kilometres.",
                 "When {actor_plural} are developers, say PR.", "Where the country is DE, say Euro.",
                 "If the industry is shipping, ask about the last voyage."):
        why = cycle.special_case({**base, "new_text": text, "persona_aware": True})
        assert why and "a condition on who the people are" in why, text
    assert cycle.special_case({**base, "new_text": "Ask it in the words of {actor_plural}, about the last {job}.",
                               "persona_aware": True}) is None


def test_a_special_case_is_recorded_by_row_and_never_written_as_a_proposal(monkeypatch, tmp_path, capsys):
    answer = json.dumps({"new_text": "If the people are night porters, say the night desk; otherwise say the front "
                                     "desk.", "why": "One. Two. Three.", "rung": "words", "persona_aware": True})
    code, out, _ = _advise(monkeypatch, tmp_path, answer)
    assert code == 0 and "REFUSED: a special case" in capsys.readouterr().out
    text = out.read_text(encoding="utf-8")
    section = text.split(f"## 1. {WEAK_ROW}", 1)[1]
    assert "**Refused -- not a proposal** (spec 081 FR-6)" in section and "Rung: **" not in section
    assert "The proposed text:" not in section and "<summary>The refused text</summary>" in section
    data = json.loads(text.split("<!-- advice:data -->", 1)[1].split("```json", 1)[1].split("```", 1)[0])
    assert "a condition on who the people are" in data["proposals"][0]["refused"]


def test_the_dry_adviser_on_the_fixture_cycle_prints_the_rule(monkeypatch, tmp_path, capsys):
    code, out, fake = _advise(monkeypatch, tmp_path, "{}", "--dry-run")
    said = capsys.readouterr().out
    assert code == 0 and fake.seen == [] and not out.exists()
    assert "## The fix is persona awareness, never a special case" in said


# ---------------------------------------------------------------------------------------- FR-7 nothing else

def test_nothing_else_moves():
    from instructions import marks as marks_mod                         # noqa: PLC0415
    assert marks_mod.MARKS_VERSION == 22                          # spec 093 moved it (L1, L5)
    ids = [r["id"] for r in rubric.criteria()]
    assert ids[:5] == list(rubric.SHARED) and rubric.G_CRITERIA == ("g1", "g2")
    assert (rubric.BAR_PCT, rubric.WEAK_ZERO_ENTRIES, rubric.WEAK_MEAN) == (90.0, 2, 1.5)
    assert readers.load_reader_config()["model"] == "claude-opus-5-5"
    r1 = next(r for r in rubric.criteria() if r["id"] == "r1")
    assert r1["0"] == "out of place, or asks what was already answered"
