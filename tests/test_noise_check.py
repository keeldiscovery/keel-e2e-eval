"""Spec 074 FR-3: `make noise-check`, the noise-capture certificate -- scored offline, no call.

The canon's own run of 2026-10-26 (keel-cloud `canon/designs/noise-capture-check-2026-10-26/results/stt-none.jsonl`,
1,260 rows of Keel's path) is read again through the moved `norm_out` and the certificate rule: with keel-cloud 136's
partial-pick read the pick-two rows are right and the bar PASSes; with the read switched off the rows read exactly as
the canon scored them and the bar FAILs on the quiet room (`clean`), the one partial-pick miss breaking its 100%.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

import pytest

from evals.noise import dataset, pipeline as pl, report as rp
from stack.config import REPO_ROOT, load_config

CANON = Path("canon") / "designs" / "noise-capture-check-2026-10-26"


def _canon() -> Path:
    root = load_config(validate=False).keel_cloud / CANON
    if not (root / "results" / "stt-none.jsonl").is_file():
        pytest.skip("keel-cloud's checkout carries no noise-capture check (before 2026-10-26)")
    return root


@pytest.fixture(scope="module")
def rows() -> list[dict]:
    path = _canon() / "results" / "stt-none.jsonl"
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


# --------------------------------------------------------------------------------- the acceptance: offline

def test_the_canons_rows_pass_with_136s_read(rows):
    scored = [pl.rescore(r) for r in rows]
    cert = rp.certificate(scored)
    assert len(rows) == 1260
    assert cert["verdict"] == "PASS", cert["line"]
    assert cert["cells"]["clean"]["closed_ok"] == 100.0
    assert all(v["closed_ok"] > 90 and v["false_support"] <= 2 and v["meaning_kept"] >= 90
               for c, v in cert["cells"].items())
    assert cert["line"].startswith("Certificate (the founder's bar, 2026-10-26") and ": PASS." in cert["line"]
    # the 0 dB cells are reported, outside the bar: the café at 0 dB is under 90% and does not fail it
    assert cert["stress"]["cafe@0"]["closed_ok"] < 90 and "outside the bar" in cert["line"]


def test_the_pick_two_rows_are_now_right(rows):
    partial = [r for r in rows if r["utterance"] == "c5"]
    assert len(partial) == 42 and sum(r["ok"] for r in partial) == 0          # the canon: asked again, every one
    scored = [pl.rescore(r) for r in partial]
    assert all(r["got"] == {"picks": [2]} and r["ok"] for r in scored if r["raw"].get("picks") == [2])
    # 41 of 42 now right; the one left is the café at 0 dB, where the babble was heard and no label named
    assert [r["id"] for r in scored if not r["ok"]] == ["c5-onyx-cafe-0"]
    changed = {r["id"] for r, s in zip(rows, map(pl.rescore, rows)) if r["ok"] != s["ok"]}
    assert changed == {r["id"] for r in partial} - {"c5-onyx-cafe-0"}          # the read moves nothing else


def test_the_read_switched_off_fails_on_the_quiet_room(rows):
    scored = [pl.rescore(r, partial_pick=False) for r in rows]
    assert [r["ok"] for r in scored] == [r["ok"] for r in rows]               # the canon's own scoring, row for row
    cert = rp.certificate(scored)
    assert cert["verdict"] == "FAIL" and cert["failing"] == "clean", cert["line"]
    assert cert["failing_faults"] == ["closed answers right 95.8% < 100%"]
    assert "the first failing cell is the quiet room (clean)" in cert["line"]


# ------------------------------------------------------------------- norm_out restates Classification.validated()

PICK_TWO, SINGLE, GATE, NUMBER = (dataset.ITEMS[k] for k in ("importance", "better", "gate", "days"))


@pytest.mark.parametrize("item, out, got", [
    # keel-cloud 136's acceptance (ClassificationTest), restated
    (PICK_TWO, {"picks": [2], "unclear": True, "reason": "named only 1"}, {"picks": [2]}),
    (PICK_TWO, {"picks": [], "unclear": True}, {"unclear": True}),
    (SINGLE, {"picks": [1], "unclear": True}, {"unclear": True}),
    (PICK_TWO, {"picks": [1, 3], "unclear": True}, {"picks": [1, 3]}),
    # the rest of validated()
    (PICK_TWO, {"picks": [9], "unclear": True}, {"unclear": True}),             # no label named: unclear wins
    (PICK_TWO, {"picks": [5, 1, 3]}, {"picks": [1, 5]}),                        # more than N: the first N said
    (PICK_TWO, {"picks": ["2", "4"]}, {"picks": [2, 4]}),                       # digits as text are numbers
    (SINGLE, {"picks": [3, 1]}, {"picks": [3]}),                               # two on a single: the first
    (SINGLE, {"picks": [2], "escape": True}, {"escape": True}),
    (GATE, {"picks": [1], "escape": True}, {"picks": [1]}),                     # no escape on the gate: dropped
    (GATE, {"picks": []}, {"unclear": True}),
    (NUMBER, {"value": 14}, {"value": 14}),
    (NUMBER, {"value": 31}, {"unclear": True}),                                 # out of range
    (NUMBER, {"value": "14"}, {"unclear": True}),                               # not a number on the wire
    (NUMBER, {"value": None, "escape": True}, {"escape": True}),
    (NUMBER, {"unclear": True, "value": 3}, {"unclear": True}),
    (SINGLE, None, {"unclear": True, "_err": True}),                            # a reply that was not the JSON
])
def test_norm_out_is_validated_restated(item, out, got):
    assert pl.norm_out(item, out) == got


def test_the_partial_pick_switch_restates_the_read_before_136():
    assert pl.norm_out(PICK_TWO, {"picks": [2], "unclear": True}, partial_pick=False) == {"unclear": True}
    assert pl.norm_out(PICK_TWO, {"picks": [2], "unclear": False}, partial_pick=False) == {"picks": [2]}


def test_the_partial_pick_is_keel_clouds_rule():
    source = (load_config(validate=False).keel_cloud / "src/main/java/com/keeldiscovery/cloud/application/interviewer"
              / "Classification.java")
    if not source.is_file():
        pytest.skip("keel-cloud's checkout has no Classification.java")
    text = source.read_text(encoding="utf-8")
    assert "if (unclear && !partialPick(item))" in text
    assert "item.kind() == SpokenItem.Kind.MULTI && item.pick() > 0" in text


# --------------------------------------------------------------------------------- the product's own calls

def _cloud(rel: str) -> str:
    path = load_config(validate=False).keel_cloud / "src/main/java/com/keeldiscovery/cloud" / rel
    if not path.is_file():
        pytest.skip(f"keel-cloud's checkout has no {rel}")
    return path.read_text(encoding="utf-8")


def test_the_classifier_is_called_as_keel_cloud_calls_it():
    source = _cloud("infrastructure/anthropic/KeelsAiClassifier.java")
    assert re.search(r"static final long MAX_TOKENS = (\d+);", source).group(1) == str(pl.MAX_TOKENS) == "400"
    assert ".temperature(0.0)" in source and pl.TEMPERATURE == 0.0
    assert pl.CLASSIFY_MODEL == "claude-haiku-4-5-20251001"
    assert 'lines.add("Answer kind: " + describe(item) + ".");' in source
    assert 'lines.add("They said: \\"" + (request.heard() == null ? "" : request.heard().strip()) + "\\"");' in source
    assert (load_config(validate=False).keel_cloud / pl.INSTRUCTION).is_file()


def test_the_transcriber_is_called_as_keel_cloud_calls_it():
    source = _cloud("infrastructure/openai/OpenAiTranscriber.java")
    assert f'MODEL = "{pl.TRANSCRIBE_MODEL}";' in source and f'PROMPT = "{pl.TRANSCRIBE_PROMPT}";' in source
    for field in ('"response_format", "json"', '"languages[]"', '"keywords[]"', '"prompt"'):
        assert field in source, field
    assert pl.hints(PICK_TWO) == PICK_TWO["options"] + ["None of these"] and pl.hints(GATE) == GATE["options"]


def test_the_user_lines_are_the_canons(rows):
    canon = (_canon() / "pipeline.py").read_text(encoding="utf-8")
    assert 'lines.append(f\'They said: "{(heard or "").strip()}"\')' in canon
    assert pl.user_prompt(PICK_TWO, " the tax one ").splitlines() == [
        "Answer kind: exactly 2 of the options.", "Options:", *[f"  {i}. {o}" for i, o in
                                                              enumerate(PICK_TWO["options"], 1)],
        'Escape option, only when they say they cannot answer: "None of these"', 'They said: "the tax one"']
    assert pl.user_prompt(NUMBER, "3").splitlines()[0] == "Answer kind: a whole number from 0 to 30."


# ------------------------------------------------------------------------------------------- the move

def test_the_dataset_and_the_page_are_the_canons_own():
    canon = _canon()
    here = REPO_ROOT / "evals" / "noise"
    assert (here / "dataset.py").read_bytes() == (canon / "dataset.py").read_bytes()
    assert (here / "page_template.html").read_bytes() == (canon / "page_template.html").read_bytes()
    for name in ("pipeline.py", "synth.py", "report.py"):
        assert (here / name).is_file() and (canon / name).is_file(), name     # moved; the canon keeps its copy


def test_the_manifest_is_the_canons_1260_samples():
    canon = json.loads((_canon() / "samples.json").read_text(encoding="utf-8"))
    ours = pl.manifest()
    assert [s["id"] for s in ours] == [s["id"] for s in canon] and len(ours) == 1260
    assert all(o["m4a"] == c["m4a"].removeprefix("audio/") for o, c in zip(ours, canon))


def test_select_takes_only_snrs_and_clean():
    picked = pl.select(pl.manifest(), only="c5-", snrs="clean,5")
    assert {s["snr"] for s in picked} == {None, 5} and all(s["id"].startswith("c5-") for s in picked)
    assert len(picked) == 2 * (1 + len(dataset.BEDS))


def test_the_samples_root_is_the_kept_set_unless_named():
    assert pl.samples_root({}) == Path.home() / "Documents/projects/keel-noise-check-2026-10-26/audio"
    assert pl.samples_root({"KEEL_NOISE_SAMPLES": "/tmp/x"}) == Path("/tmp/x")


def test_the_keys_are_refused_by_name_never_shown():
    with pytest.raises(SystemExit) as refused:
        pl.keys_from({"KEEL_OPENAI_API_KEY": "sk-secret-123"})
    assert "KEEL_ANTHROPIC_API_KEY" in str(refused.value) and "sk-secret-123" not in str(refused.value)
    assert pl.keys_from({"KEEL_OPENAI_API_KEY": "a", "KEEL_ANTHROPIC_API_KEY": "b"}) == {"openai": "a",
                                                                                       "anthropic": "b"}


def test_the_paid_command_runs_nowhere_but_its_own_target():
    make = (REPO_ROOT / "Makefile").read_text(encoding="utf-8")
    targets = {m.group(1): m.group(2) for m in re.finditer(r"^([a-z-]+):[^\n]*\n((?:\t[^\n]*\n)+)", make, re.M)}
    assert "evals.noise" in targets["noise-check"] and "KEEL_ANTHROPIC_API_KEY" in targets["noise-check"]
    for name in ("eval", "unit", "eval-all", "matrix-check"):
        assert "noise" not in targets.get(name, ""), name
    assert not list((REPO_ROOT / "evals" / "noise").glob("test_*.py"))         # nothing `make eval` would collect
    for path in (REPO_ROOT / "matrix").glob("*"):
        if path.is_file():
            assert "noise" not in path.read_text(encoding="utf-8", errors="ignore"), path


# --------------------------------------------------------------------------------------------- the files

def test_the_run_folder_carries_the_certificate(rows, tmp_path):
    run_dir = tmp_path / "runs" / "20261027T120000Z-noise-check"
    run_dir.mkdir(parents=True)
    with (run_dir / rp.RESULTS).open("w", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(pl.rescore(r)) + "\n")
    cert = rp.write(run_dir, root=None, selection={"only": None}, keel_cloud_sha="409d38d1")
    assert cert["verdict"] == "PASS"
    md = (run_dir / rp.MARKDOWN).read_text(encoding="utf-8")
    for heading in ("## The rooms", "## The controls", "## The misses"):
        assert heading in md, heading
    assert cert["line"] in md and "| cafe@0 (outside the bar) |" in md
    assert "| Construction site | 100.0% |" in md
    summary = json.loads((run_dir / rp.SUMMARY).read_text(encoding="utf-8"))
    assert summary["certificate"]["verdict"] == "PASS" and summary["pass"]["n"] == 1260
    row = (run_dir / rp.REGISTER_ROW).read_text(encoding="utf-8")
    assert row.startswith("| 20261027T120000Z | 409d38d1 | PASS | 100.0% |")
    register = (tmp_path / "runs" / rp.REGISTER).read_text(encoding="utf-8")
    assert register.startswith(rp.REGISTER_HEAD) and row in register
    page = (run_dir / "page" / "index.html").read_text(encoding="utf-8")
    assert "__DATA__" not in page and '"stt-none"' in page


def test_a_partial_run_certifies_nothing_and_a_bad_cell_is_named(rows):
    scored = [pl.rescore(r) for r in rows]
    partial = rp.certificate([r for r in scored if r["snr"] in (None, 5)])
    assert partial["verdict"] == "INCOMPLETE" and "construction@20" in partial["unmeasured"]
    wrong = [dict(r, ok=False, definite=True, false_support=True) if r["bed"] == "music" and r["snr"] == 10
             and r["control"] != "free text" and r["utterance"] in ("g1", "n1") else r for r in scored]
    cert = rp.certificate(wrong)
    assert cert["verdict"] == "FAIL" and cert["failing"] == "music@10"
    assert any("confident wrong" in f for f in cert["failing_faults"])
    lost = [dict(r, ok=False) if r["bed"] == "wind" and r["snr"] == 20 and r["control"] == "free text" else r
            for r in scored]
    cert = rp.certificate(lost)
    assert cert["failing"] == "wind@20" and any("stories' meaning kept" in f for f in cert["failing_faults"])
    stressed = [dict(r, ok=False) if r["snr"] == 0 else r for r in scored]
    assert rp.certificate(stressed)["verdict"] == "PASS"                     # 0 dB never gates


def test_a_story_is_scored_without_jiwer():
    exp = dataset.UTTERANCES[24][3]
    good = pl.score_story(exp, "So the invoice was 45 days late, and I had to call them three times before anyone "
                               "picked up, and in the end they said they never got it.")
    assert good["meaning_kept"] and good["wer"] == 0.0
    bad = pl.score_story(exp, "So the invoice was late and I called them.")
    assert not bad["meaning_kept"] and bad["wer"] > 0.5
    assert pl.wer("a b c", "a x c") == pytest.approx(1 / 3)
