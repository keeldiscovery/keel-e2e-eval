"""Decided before (spec 087): the founder's decisions are recorded in `quality/decisions.toml`, and a weak row he has
already decided is snoozed and listed, not advised again -- with no model, no stack, no network and no key.

The fake records are spec 079's fixture cycle (`tests/fixtures/quality/cycle/`: one weak row, `PROBLEM · respondent ·
problem.importance · item`, fixed at a registry row) with a decisions file written per test; the acceptance's dry run
reads the real cycle `quality/cycles/20261028-f48f256.md` and the real file of record.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

import pytest

from quality import cycle, decisions as dec, table
from tests import test_quality_cycle_079 as c079

REPO = Path(__file__).resolve().parent.parent
RECORD = c079.RECORD
CLOUD = c079.CLOUD
WEAK_ROW = c079.WEAK_ROW
F48 = REPO / "quality" / "cycles" / "20261028-f48f256.md"
F48_ADVICE = REPO / "quality" / "cycles" / "20261028-f48f256-advice.md"

ROW = {"scope": "PROBLEM", "audience": "respondent", "dimension": "problem.importance", "screen": "item"}


def entry(**kw) -> dict:
    base = {"id": "D-1", "cycle": "20261101-abcdef1", "proposals": [1], "row": dict(ROW),
            "fix": "dimension-registry.json", "decision": "declined", "until": "never",
            "why": "FIXTURE-WHY-ONE: the founder said no."}
    base.update(kw)
    return base


def _toml_value(v) -> str:
    if isinstance(v, dict):
        return "{ " + ", ".join(f"{k} = {_toml_value(x)}" for k, x in v.items()) + " }"
    return json.dumps(v, ensure_ascii=False)


def write(path: Path, *entries: dict) -> Path:
    blocks = ["[[decision]]\n" + "".join(f"{k} = {_toml_value(v)}\n" for k, v in e.items()) for e in entries]
    path.write_text("\n".join(blocks), encoding="utf-8")
    return path


class Never:
    """A runner that fails the test if anything is called: a dry run and a snoozed row send nothing."""

    def __init__(self):
        self.seen = []

    def __call__(self, argv, **kw):
        self.seen.append(argv)
        raise AssertionError(f"nothing is called: {argv}")


def dry(capsys, decisions_path: Path, record: Path = RECORD) -> tuple[int, str]:
    runner = Never()
    code = cycle.advise(["--cycle", str(record), "--cloud", str(CLOUD), "--decisions", str(decisions_path),
                         "--dry-run"], runner=runner)
    assert runner.seen == []
    return code, capsys.readouterr().out


# ------------------------------------------------------------------------------------------------ FR-1 the record

def test_the_file_of_record_parses_and_every_row_names_scored_scopes_and_screens():
    found = dec.load(dec.DECISIONS_PATH)
    # spec 089 FR-6: the five recorded 0s, held for the founder (D-2026-10-30-01, spec-merged with no spec yet)
    # cycle 3 (2026-10-30, the founder: the top three consistent causes): D-2026-10-30-02 (167), -03 (168), -04 (web 146);
    # -05 (declined, never): the own-AI door's lock hint and greyed formats are that road's true screens, not faults
    assert len(found) == 25 and [d["id"] for d in found] == [f"D-2026-10-29-{i:02d}" for i in range(1, 21)] + [
        f"D-2026-10-30-{i:02d}" for i in range(1, 6)]
    records = {p.stem for p in cycle.record_files(REPO / "quality" / "cycles")}
    for d in found:
        assert d["cycle"] in records, f"{d['id']} names a committed cycle record"
        assert set(d["_row"]["scope"] or cycle.SCOPES) <= set(cycle.SCOPES), d["id"]
        assert set(d["_row"]["audience"] or ("founder",)) <= {"founder", "respondent"}, d["id"]
        assert set(d["_row"]["screen"] or dec.SCREENS) <= set(dec.SCREENS), d["id"]
        assert d["decision"] != "taken" or d.get("spec"), f"{d['id']}: a taken decision names its spec"
        assert d["why"].strip()
    assert {d["decision"] for d in found} == {"taken", "declined", "held"}
    assert {d["until"] for d in found} == {"spec-merged", "never", "20261028-f48f256"}
    # spec 085 FR-4 (087's duty, written on master at c474dfe): the coordinator marks a spec-merged entry `merged` when
    # the spec it names lands -- nothing had when the file was written; eight have since, D-01 keel-cloud 149's
    merged = {d["id"]: d["merged"] for d in found if d.get("merged")}
    assert merged == {"D-2026-10-29-01": "73426a67", "D-2026-10-29-02": "1b33643f", "D-2026-10-29-03": "0eb15f8f",
                      "D-2026-10-29-05": "21395ab0", "D-2026-10-29-13": "e3d34831", "D-2026-10-29-14": "e3d34831",
                      "D-2026-10-30-01": "48621fd",  # 090 FR-3: the five 0s sent as 1 (2026-10-30)
                      "D-2026-10-29-15": "1cf2ebc3", "D-2026-10-29-19": "078fe157",
                      # marked 2026-10-30 after cycle 3: web 130 (D-08, D-16), web 134 (D-17), the open link's specs (D-10)
                      "D-2026-10-29-08": "51c3c4a", "D-2026-10-29-16": "51c3c4a", "D-2026-10-29-17": "e5577d2",
                      "D-2026-10-29-10": "01048e86"}
    for d in found:
        if d.get("merged"):
            assert d["decision"] == "taken" and d["until"] == "spec-merged", d["id"]


def test_the_screens_are_the_ones_the_cycle_scores():
    kinds = set()
    for path in [*(REPO / "quality" / "scores").rglob("*.json"), *c079.SCORES.rglob("*.json")]:
        body = json.loads(path.read_text(encoding="utf-8"))
        kinds |= {s["kind"] for s in body.get("screens") or []}
        if body.get("insights"):
            kinds.add("insights")
    assert kinds and kinds <= set(dec.SCREENS), sorted(kinds - set(dec.SCREENS))
    assert set(table._FOUNDER_FILES) <= set(dec.SCREENS)


@pytest.mark.parametrize("change, said", [
    ({"why": None}, "lacks why"),
    ({"decision": "maybe"}, "decision 'maybe' is not one of taken, declined, held"),
    ({"until": "soon"}, "until 'soon' is not one of spec-merged, never or a cycle id"),
    ({"row": {**ROW, "scope": "EVERYTHING"}}, "row.scope names EVERYTHING, which the cycle does not score"),
    ({"row": {**ROW, "audience": "investor"}}, "row.audience names investor, which the cycle does not score"),
    ({"row": {**ROW, "screen": ["item", "homepage"]}}, "row.screen names homepage, which the cycle does not score"),
    ({"row": {**ROW, "dimension": "importance"}}, "row.dimension names importance"),
    ({"row": {"scope": "*", "audience": "*", "screen": "*"}}, "row must carry exactly scope, audience, dimension"),
    ({"row": {**ROW, "screen": ["*", "item"]}}, "`*` stands alone"),
    ({"decision": "taken", "until": "spec-merged"}, "a taken decision names the spec(s) it became"),
    ({"merged": "abc1234"}, "merged ends a spec-merged snooze only"),
    ({"untill": "never"}, "carries untill, which no decision has"),
    ({"cycle": "last week"}, "is not a cycle id"),
    ({"fix": []}, "fix is [] -- a string, a list of strings, or `*`"),
])
def test_a_file_that_is_not_the_shape_is_refused_by_name(tmp_path, change, said):
    e = {k: v for k, v in {**entry(), **change}.items() if v is not None}
    with pytest.raises(dec.DecisionsError) as raised:
        dec.load(write(tmp_path / "decisions.toml", e))
    assert said in str(raised.value)


def test_an_id_used_twice_is_refused_and_no_file_is_no_decision(tmp_path):
    with pytest.raises(dec.DecisionsError, match="the id D-1 is used twice"):
        dec.load(write(tmp_path / "d.toml", entry(), entry()))
    assert dec.load(tmp_path / "none.toml") == []


def test_a_bad_file_refuses_the_adviser_before_anything(tmp_path, capsys):
    bad = write(tmp_path / "d.toml", entry(decision="maybe"))
    assert cycle.advise(["--cycle", str(RECORD), "--cloud", str(CLOUD), "--decisions", str(bad), "--dry-run"]) == 2
    err = capsys.readouterr().err
    assert "make quality-advise refuses: the decisions file" in err and "is not the shape spec 087 FR-1 reads" in err
    assert "decision 'maybe' is not one of taken, declined, held" in err


# ------------------------------------------------------------------------------------------------ FR-2 the match

def _row(**kw):
    base = {"scope": "PROBLEM", "audience": "respondent", "dimension": "problem.importance", "kind": "item",
            "weak_on": ["r2"], "fix": {"category": "registry row", "place": "problem.importance's respondent wording, "
                                                                              "else the code transform (no model)"}}
    base.update(kw)
    return base


def test_the_row_and_the_fix_match_as_sets_with_a_star_and_a_dash(tmp_path):
    def one(**kw):
        return dec.load(write(tmp_path / "d.toml", entry(**kw)))[0]
    assert dec.row_matches(one(), _row())
    assert dec.row_matches(one(row={"scope": "*", "audience": "*", "dimension": "*", "screen": "*"}), _row())
    assert dec.row_matches(one(row={**ROW, "scope": ["SOLUTION", "PROBLEM"]}), _row())
    assert not dec.row_matches(one(row={**ROW, "scope": "SOLUTION"}), _row())
    assert not dec.row_matches(one(row={**ROW, "dimension": "-"}), _row()), "`-` is a row with no dimension"
    assert dec.row_matches(one(row={**ROW, "dimension": "-", "screen": "screener"}),
                           _row(dimension="-", kind="screener"))
    screener = {"category": "shared file", "place": "respondent-questions.md (the story clause, the screener question)"}
    context = {"category": "shared file", "place": "context-interpret.md, and code (ReadBack, Qualifiers)"}
    page = {"category": "no model", "place": "the page's own words (keel-web / keel-cloud code)"}
    assert dec.fix_matches(one(fix="dimension-registry.json"), _row()["fix"]), "the registry file is a registry row"
    assert dec.fix_matches(one(fix="Registry row"), _row()["fix"]), "the category itself, case aside"
    assert dec.fix_matches(one(fix=["asked.md", "respondent-questions.md"]), screener)
    assert dec.fix_matches(one(fix="context-interpret.md"), context)
    assert dec.fix_matches(one(fix="the page's own words"), page)
    assert dec.fix_matches(one(fix="*"), page)
    assert not dec.fix_matches(one(fix="questions.md"), screener), "a whole name, not a piece of one"
    assert not dec.fix_matches(one(fix="dimension-registry.json"), screener)
    assert not dec.fix_matches(one(fix="a third persona option"), page), "a free label snoozes nothing"


def test_never_snoozes_lists_and_sends_nothing(tmp_path, capsys):
    code, said = dry(capsys, write(tmp_path / "d.toml", entry()))
    assert code == 0 and "[1/" not in said and "FIXTURE-RESPONDENT-GUIDANCE" not in said
    assert "## Decided before (1)" in said
    assert (f"- {WEAK_ROW} -- **D-1** declined, for good: FIXTURE-WHY-ONE: the founder said no.") in said
    assert ("cycle 20261101-abcdef1: 1 weak row(s), every one decided before (quality/decisions.toml, spec 087) -- "
            "nothing to advise, no call made") in said


@pytest.mark.parametrize("until, snoozed", [("20261101-abcdef1", True), ("20261231-0000000", True),
                                            ("20261031-fffffff", False)])
def test_a_cycle_id_snoozes_through_that_cycle(tmp_path, capsys, until, snoozed):
    code, said = dry(capsys, write(tmp_path / "d.toml", entry(decision="held", until=until)))
    assert code == 0
    if snoozed:
        assert f"**D-1** held, through cycle {until}" in said and "[1/1]" not in said
    else:
        assert f"[1/1] {WEAK_ROW}" in said and "Decided before" not in said
        assert "dry run: 1 adviser prompt(s) for cycle 20261101-abcdef1; no call made, nothing written" in said


def test_spec_merged_snoozes_until_merged_is_written_then_the_row_competes(tmp_path, capsys):
    taken = entry(decision="taken", until="spec-merged", spec=["keel-cloud 999"], why="FIXTURE-TAKEN-WHY")
    code, said = dry(capsys, write(tmp_path / "d.toml", taken))
    assert code == 0 and "[1/1]" not in said
    assert f"- {WEAK_ROW} -- **D-1** taken (keel-cloud 999), until its spec is merged: FIXTURE-TAKEN-WHY" in said
    code, said = dry(capsys, write(tmp_path / "d.toml", {**taken, "merged": "abc1234"}))
    assert code == 0 and f"[1/1] {WEAK_ROW}" in said and "FIXTURE-RESPONDENT-GUIDANCE" in said
    assert "Decided before" not in said and "FIXTURE-TAKEN-WHY" not in said, "it competed: not listed"


def test_a_decision_on_another_row_or_another_fix_snoozes_nothing(tmp_path, capsys):
    other = entry(row={**ROW, "scope": "SOLUTION"})
    label = entry(id="D-2", fix="the importance control")
    code, said = dry(capsys, write(tmp_path / "d.toml", other, label))
    assert code == 0 and f"[1/1] {WEAK_ROW}" in said and "Decided before" not in said


def _compose(decisions):
    """079's fixture record (`compose_the_fixture`'s arguments), composed with these decisions."""
    return cycle.compose(c079.studies_of_the_fixture(), name="20261101-abcdef1",
                         why="the registry's Importance row moved (keel-cloud 150)", door="host", cloud_sha="abcdef1",
                         web_sha="1234567", started="2026-11-01T10:00:00+00:00", ended="2026-11-01T11:00:00+00:00",
                         seconds=3600.0, cfg=cycle.load_config(), baseline_path=c079.BASELINE,
                         cycles_dir=c079.FX / "cycles", cloud_branch="master", scores_dir=c079.SCORES_REL,
                         entries_arg="08-fresco,09-karsa", decisions=decisions)


def test_the_record_lists_the_snoozed_rows_under_decided_before(tmp_path):
    text, data = _compose(dec.load(write(tmp_path / "d.toml", entry())))
    assert data["weak_rows"] == [WEAK_ROW], "the measurement is kept whole"
    assert data["decided_before"] == [{"row": WEAK_ROW, "weak_on": ["r2", "r3", "r4"], "decisions": [
        {"id": "D-1", "decision": "declined", "until": "never", "why": "FIXTURE-WHY-ONE: the founder said no."}]}]
    assert "## Weak rows (1: 0 to advise, 1 decided before)" in text
    assert "- none to advise: every weak row was decided before (below)" in text
    assert "## Decided before (1) -- snoozed by `quality/decisions.toml` (spec 087), not sent to the adviser" in text
    assert f"- {WEAK_ROW} -- **D-1** declined, for good: FIXTURE-WHY-ONE" in text
    assert "1. **Advise** (paid, one call per weak row not decided before: 0)" in text
    (tmp_path / "20261101-abcdef1.md").write_text(text, encoding="utf-8")
    assert cycle.load_record(tmp_path / "20261101-abcdef1.md")["decided_before"] == data["decided_before"]
    plain, plain_data = _compose([])
    assert plain == RECORD.read_text(encoding="utf-8") and "decided_before" not in plain_data, \
        "with nothing decided, the record is 079's to the byte"


# ------------------------------------------------------------------------------------------------ FR-3 the adviser

def test_the_adviser_prompt_carries_the_declined_whys_on_the_row(tmp_path):
    found = dec.load(write(tmp_path / "d.toml",
                           entry(id="D-1", row={"scope": "*", "audience": "*", "dimension": "*", "screen": "*"},
                                 fix="the no-number rule", why="FIXTURE-STAR-WHY: no digits in the statement, ever."),
                           entry(id="D-2", fix="the occasion as a stretch of work",
                                 why="FIXTURE-ROW-WHY: the occasion stays one noun everywhere."),
                           entry(id="D-3", row={**ROW, "scope": "SOLUTION"}, why="FIXTURE-OTHER-ROW-WHY"),
                           entry(id="D-4", decision="taken", until="spec-merged", spec="keel-cloud 1",
                                 why="FIXTURE-TAKEN-WHY"),
                           entry(id="D-5", until="20261031-fffffff", why="FIXTURE-ENDED-WHY")))
    files, rows = c079._weak()
    declined = dec.declined_for(rows[0], found, "20261101-abcdef1")
    assert [d["id"] for d in declined] == ["D-1", "D-2"]
    prompt = cycle.adviser_prompt(rows[0], files, cloud=CLOUD, cfg=cycle.load_config(), sha="abcdef1",
                                  declined=declined)
    assert "{{" not in prompt and "## What the founder has already said no to" in prompt
    assert "FIXTURE-STAR-WHY: no digits in the statement, ever." in prompt
    assert "FIXTURE-ROW-WHY: the occasion stays one noun everywhere." in prompt
    assert "- D-1 -- on scope any; audience any; dimension any; screen any; what was proposed: the no-number rule" \
        in prompt
    for absent in ("FIXTURE-OTHER-ROW-WHY", "FIXTURE-TAKEN-WHY", "FIXTURE-ENDED-WHY"):
        assert absent not in prompt, absent
    assert '"reopens": [] | ["<decision id>", ...]' in prompt
    bare = cycle.adviser_prompt(rows[0], files, cloud=CLOUD, cfg=cycle.load_config(), sha="abcdef1")
    assert "(The founder has declined nothing on this row.)" in bare


def _two_rows(monkeypatch):
    """The fixture's weak row, and a second one at the gate (a shared file), so one is advised and one snoozed."""
    real = cycle.weak_rows

    def two(files):
        rows = real(files)
        gate = {**rows[0], "dimension": "problem.prevalence", "kind": "gate",
                "fix": {"category": "shared file", "place": "respondent-questions.md (the story clause, the screener "
                                                            "question)"}}
        return rows + [gate]
    monkeypatch.setattr(cycle, "weak_rows", two)


def _advise(monkeypatch, tmp_path, answer, decisions_path):
    fake = c079.FakeAdviser(answer)
    monkeypatch.setattr(cycle.readers.Reader, "available", lambda self: True)
    monkeypatch.setattr(cycle, "RUNS_DIR", tmp_path / "runs")
    out = tmp_path / "advice.md"
    code = cycle.advise(["--cycle", str(RECORD), "--cloud", str(CLOUD), "--out", str(out), "--decisions",
                         str(decisions_path)], runner=fake)
    return code, out, fake


GATE_ROW = "PROBLEM · respondent · problem.prevalence · gate"


def test_the_advice_page_lists_the_snoozed_rows_at_its_end_and_counts_only_the_advised(monkeypatch, tmp_path):
    _two_rows(monkeypatch)
    snooze = entry(id="D-9", row={**ROW, "dimension": "problem.prevalence", "screen": "gate"},
                   fix="respondent-questions.md", decision="taken", until="spec-merged", spec="keel-cloud 153",
                   why="FIXTURE-GATE-WHY")
    competed = entry(id="D-8", decision="taken", until="spec-merged", spec="keel-cloud 152", merged="abc1234",
                     why="FIXTURE-MERGED-WHY")
    answer = json.dumps({"new_text": "Which two of these came first?", "why": "One. Two. Three.", "rung": "words",
                         "persona_aware": True, "reopens": []})
    code, out, fake = _advise(monkeypatch, tmp_path, answer, write(tmp_path / "d.toml", snooze, competed))
    assert code == 0 and len(fake.seen) == 2, "the probe, then one call: the gate row is snoozed"
    text = out.read_text(encoding="utf-8")
    assert "Spec 079 FR-4. 1 weak row(s) of `quality/cycles/20261101-abcdef1.md`" in text
    assert "1 more decided before, listed at the end (spec 087)" in text
    assert f"## 1. {WEAK_ROW}" in text and "## 2." not in text
    tail = text.split("## Decided before (1)", 1)[1]
    assert f"- {GATE_ROW} -- **D-9** taken (keel-cloud 153), until its spec is merged: FIXTURE-GATE-WHY" in tail
    assert "FIXTURE-MERGED-WHY" not in text, "a taken decision whose spec merged is not listed: the row competed"
    assert text.index("## Decided before") > text.index(f"## 1. {WEAK_ROW}")
    data = json.loads(text.split("<!-- advice:data -->", 1)[1].split("```json", 1)[1].split("```", 1)[0])
    assert [s["row"] for s in data["decided_before"]] == [GATE_ROW]


def test_a_proposal_that_reopens_a_declined_decision_is_refused_naming_it(monkeypatch, tmp_path):
    declined = entry(id="D-7", fix="a third persona option", why="FIXTURE-DECLINED-WHY: leave it as it is.")
    answer = json.dumps({"new_text": "Add a third option.", "why": "y", "rung": "words", "persona_aware": True,
                         "reopens": ["D-7"]})
    code, out, fake = _advise(monkeypatch, tmp_path, answer, write(tmp_path / "d.toml", declined))
    assert code == 0 and len(fake.seen) == 2
    text = out.read_text(encoding="utf-8")
    assert "**Refused -- not a proposal** (spec 087 FR-3)" in text
    assert "it reopens what the founder has already declined: D-7 (FIXTURE-DECLINED-WHY: leave it as it is.)" in text
    assert "Add a third option." in text and "Rung: **words**" not in text


def test_a_proposal_that_does_not_say_what_it_reopens_is_not_read_when_a_decline_was_quoted(monkeypatch, tmp_path):
    declined = entry(id="D-7", fix="a third persona option")
    answer = json.dumps({"new_text": "x", "why": "y", "rung": "words", "persona_aware": True})
    code, out, _ = _advise(monkeypatch, tmp_path, answer, write(tmp_path / "d.toml", declined))
    assert code == 0 and "**No proposal**: the answer could not be read (reopens must be a list" in out.read_text()
    assert cycle.parse_advice(answer)["reopens"] == [], "with nothing declined quoted, an answer without it reads"
    with pytest.raises(cycle.rubric.RubricError, match="reopens"):
        cycle.parse_advice(json.dumps({"new_text": "x", "why": "y", "rung": "words", "persona_aware": True,
                                       "reopens": "D-7"}))


# ------------------------------------------------------------------------------------------------ the acceptance

def test_the_dry_advise_on_cycle_f48f256_snoozes_every_weak_row_and_sends_nothing(capsys, tmp_path):
    """The acceptance: every weak row of cycle 20261028-f48f256 is snoozed under a decision of 2026-10-29 (the whole
    page was decided), each by a decision that names its advice number, and nothing is sent. Spec 085 FR-4: read on the
    file as it was written (no `merged` mark yet); the file of record, with eight marked since, is the next test's."""
    unmerged = re.sub(r'(?m)^merged = "[0-9a-f]+"\n', "", dec.DECISIONS_PATH.read_text(encoding="utf-8"))
    assert "merged = " not in unmerged
    as_written = tmp_path / "decisions.toml"
    as_written.write_text(unmerged, encoding="utf-8")
    code, said = dry(capsys, as_written, record=F48)
    assert code == 0
    listed = re.findall(r"^- ((?:COMMERCIAL|PROBLEM|SOLUTION) · .+?) -- (.+)$", said, re.M)
    advised = re.findall(r"^## (\d+)\. (.+?) -- weak on", F48_ADVICE.read_text(encoding="utf-8"), re.M)
    assert len(listed) == len(advised) == 62
    assert [row for row, _ in listed] == [row for _, row in advised], "every row of the advice, in its order"
    found = {d["id"]: d for d in dec.load()}
    for (number, row), (_, said_of) in zip(advised, listed):
        ids = re.findall(r"\*\*(D-2026-10-29-\d\d)\*\*", said_of)
        assert ids, row
        assert any(int(number) in found[i]["proposals"] for i in ids), f"{row} (proposal {number}): {ids}"
    assert "cycle 20261028-f48f256: 62 weak row(s), every one decided before" in said and "[1/" not in said


def test_a_merged_decision_ends_its_snooze_on_the_file_of_record(capsys):
    """Spec 085 FR-4 (087 FR-2's `until = "spec-merged"`): with the eight `merged` marks of master, the rows decided only
    by a merged spec are sent to the adviser again (45 prompts, none made on a dry run) and the 17 decided by a
    declined, held or unmerged entry stay snoozed -- each listed by an entry still active. Re-pinned 2026-10-30: the
    founder widened D-2026-10-29-04 (the no-number rule) from COMMERCIAL to every scope, so the PROBLEM and SOLUTION
    problem-seed rows it now covers join the list: 15 -> 17."""
    code, said = dry(capsys, dec.DECISIONS_PATH, record=F48)
    assert code == 0
    listed = re.findall(r"^- ((?:COMMERCIAL|PROBLEM|SOLUTION) · .+?) -- (.+)$", said, re.M)
    # cycle 3 (2026-10-30): D-2026-10-30-02 (idea, solution-card, solution-seed, every scope) and -03 (context,
    # context-card) take rows of this cycle too, and D-08/D-16/D-17/D-10 are marked merged: 17 -> 19 snoozed, 45 -> 43 sent
    assert len(listed) == 19
    found = {d["id"]: d for d in dec.load()}
    for row, said_of in listed:
        ids = re.findall(r"\*\*(D-2026-10-\d\d-\d\d)\*\*", said_of)
        assert ids and not any(found[i].get("merged") for i in ids), row
    assert "dry run: 43 adviser prompt(s) for cycle 20261028-f48f256; no call made, nothing written; 19 weak row(s) " \
           "decided before, not sent" in said
    assert "[1/43] COMMERCIAL · founder · - · context" in said, "149's row (D-01, merged) goes back to the adviser"


def test_the_runbook_and_the_agents_file_carry_the_decisions():
    text = (REPO / "quality" / "CYCLE.md").read_text(encoding="utf-8")
    step2 = text.split("## Step 2", 1)[1].split("## Step 3", 1)[0]
    step3 = text.split("## Step 3", 1)[1].split("## Step 4", 1)[0]
    for step in (step2, step3):
        assert "quality/decisions.toml" in step and "Decided before" in step
    flat = " ".join(step3.split())
    assert 'writes `merged = "<sha>"` on that entry' in flat
    assert "his decisions to `quality/decisions.toml` before the next advise" in flat
    agents = (REPO / "AGENTS.md").read_text(encoding="utf-8")
    assert "**Decided before**" in agents and "spec `087-decided-before`" in agents
