"""Spec 089 FR-1: corpus revision 19 (keel-cloud 159, keel-cloud-docs `1cf2ebc3`), stackless; and what specs 067, 068,
080 and 086 built on revisions 15 to 18, held at 19.

**Rule D19**, the eval's own diff: every entry read beside its revision-18 record (keel-cloud's test mirrors
`corpus-r18/` and `backtest-r18/`), every leaf difference one of 159's edits -- the revision line everywhere (the header
is a comment, so the parsed tree holds no other trace of it); Relative advantage's row, its control
(`benefit_with_advantages` -> `scale_four`) and codes (the three -> the four); every person's Relative advantage pick moved
by **the one rule** (`registry.from_three`: positive with a benefit ticked a lot better, positive with none a little
better, neutral no difference, negative worse; the chip as it was); and on a golden entry the row's `optionCounts`
added -- and never a standing, drift, inside, n or verdict (`expected` reads as revision 18's but for that field).
**D18, D17 and D16 stay as the record**, mirror against mirror: 152's eight belief fields and eleven rate beliefs
(`corpus-r17/` + `backtest-r17/` beside `corpus-r18/` + `backtest-r18/`), 147's one Buyer and payer row (`-r16/` beside
`-r17/`) and 129's 112 Commitment picks (`-r15/` beside `-r16/`). And **the cloud's own checker** `check_corpus_r19.py`
prints OK on all 35. **Rule Q** (`check_corpus_r15.py`'s, mirrored by the reader) still holds: a person's `condition` is
YES or NO, on the primary link only, where the context records a condition. The mirrors and the checker are
keel-cloud's; where its checkout lacks them the tests skip by name (judgement call 4 of 067's tasks.md).
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest
import yaml

from harness import vectors_script as vs
from instructions import corpus as corpus_mod
from instructions import registry as registry_mod
from stack.config import load_config
from tests import v9_fixtures as fx

KEEL_CLOUD = Path(load_config(validate=False).keel_cloud)
MIRROR = KEEL_CLOUD / "src" / "test" / "resources" / "keel"
SIM = KEEL_CLOUD / "canon" / "designs" / "measured-beliefs" / "sim" / "check_corpus_r19.py"

#: keel-cloud 159 (`check_corpus_r19.py`'s D19): Relative advantage, its row and its picks.
RA = "solution.relative_advantage"
R19_ROW = ("respondent_questions", RA)
R19_CODES = ["a_lot_better", "a_little_better", "no_difference", "worse"]
#: 159 tasks.md T018 / the diff table: the golden seven's 71 non-escape picks, per entry; the 28 back-tests' 361 (267 a
#: lot better, 0 a little better, 73 no difference, 21 worse).
R19_GOLDEN_PICKS = {"01-countly": 10, "02-compliancelog": 10, "03-lullaby": 10, "04-linerly": 10, "05-paidly": 11,
                    "06-repeatline": 11, "07-mulchrun": 9}
R19_BACKTEST_PICKS = {"a_lot_better": 267, "a_little_better": 0, "no_difference": 73, "worse": 21}
#: 159's *The rows*: each golden row's optionCounts as the engine recounts them (a lot, a little, no difference, worse).
R19_OPTION_COUNTS = {"01-countly": (6, 0, 2, 0), "02-compliancelog": (4, 0, 5, 0), "03-lullaby": (6, 0, 2, 0),
                     "04-linerly": (2, 0, 6, 0), "05-paidly": (6, 0, 3, 0), "06-repeatline": (3, 0, 6, 0),
                     "07-mulchrun": (5, 0, 2, 0)}
#: keel-cloud 152 T005 / T008 (`check_corpus_r18.py`'s `R18_GOLDEN`): the eight fields the seven templates move on a
#: golden entry, `founder_calibration.<row>.<field>`.
R18_GOLDEN = {("problem.prevalence", "belief_phrase"), ("problem.prevalence", "belief_sentence"),
              ("problem.importance", "belief_sentence"), ("problem.current_solution_satisfaction", "belief_sentence"),
              ("solution.compatibility", "belief_sentence"), ("solution.relative_advantage", "belief_sentence"),
              ("solution.relative_advantage", "belief_phrase"), ("commercial.commitment", "belief_sentence")}
#: 152 T009 (`R18_BACKTEST`): the rate cost's belief, on the eleven back-test entries whose cost is a RATE.
R18_BACKTEST = {("commercial.existing_sacrifice", "belief_sentence")}
R18_RATE_ENTRIES = {"09-karsa", "10-palus", "12-transload", "13-aircaps", "17-expanse", "18-careforce", "19-veles",
                    "20-lemma", "21-codyco", "23-taiga", "26-cubic"}
#: 152 T005: Prevalence's five phrases, the bin's share (recorded capitalised, 152's judgement call 8).
R18_PREVALENCE = ("Under 2 in 10", "2 to 3 in 10", "4 to 5 in 10", "6 to 7 in 10", "At least 8 in 10")
#: keel-cloud 147 T001 (`check_corpus_r17.py`'s `R17_ROW`): the one row revision 17 moved, field by field.
R17_ENTRY = "02-compliancelog"
R17_ROW = ("expected", "standings", "commercial.buyer_payer_alignment")
R17_FIELDS = {"status": ("PEOPLE_DISAGREE", "HOLDING_UP"), "drift": ("both", "none"), "inside": (5, 7),
              "outside": (4, 2)}
#: keel-cloud 129 tasks.md T028 (FR-12): the `yes_after_trying` -> `yes_start` picks per back-test entry, 112 in all.
MOVED_PICKS = {"08-fresco": 2, "09-karsa": 6, "10-palus": 2, "11-issen": 7, "12-transload": 2, "13-aircaps": 8,
               "14-code-four": 2, "15-voltair": 2, "16-pairio": 2, "17-expanse": 1, "18-careforce": 3, "19-veles": 3,
               "20-lemma": 2, "21-codyco": 3, "22-andy-ai": 3, "23-taiga": 6, "24-probo": 6, "25-bidflow": 2,
               "26-cubic": 2, "27-blacksmith": 2, "28-relvy-ai": 2, "29-risklytics": 6, "30-realroots": 6,
               "31-understood-care": 6, "32-frizzle": 7, "33-cardboard": 6, "34-wideframe": 7, "35-candle": 6}
#: 129 FR-12: Issen's seven, named.
ISSEN_SEVEN = {"Caleb Nguyen", "Jin-ho Park", "Farida Haque", "Imani Brooks", "Arjun Kapoor", "Tobias Wren",
               "Priya Natarajan"}
#: 128 FR-11 / FR-14: the entries whose context records the segment's condition, and who answers it NO (r15, kept).
CONDITIONS = {"11-issen": ("are past the beginner stage", {"Nikos Ferrante"}),
              "18-careforce": ("work outreach lists by phone", {"Olga Petrenko", "Miguel Ferreira"})}
#: 128 FR-11: 12-transload's two managers who opt in to the pilot.
PILOTS = {"12-transload": {"Nadine Fournier", "Oluwaseun Adebayo"}}
COMMITMENT = "commercial.commitment"
_ABSENT = object()


def _walk(before, after, path, out):
    """`check_corpus_r18.py`'s `_walk`: every leaf that differs, a key or index absent on one side named `_ABSENT`."""
    if isinstance(before, dict) and isinstance(after, dict):
        for k in list(before) + [k for k in after if k not in before]:
            _walk(before.get(k, _ABSENT), after.get(k, _ABSENT), path + (k,), out)
    elif isinstance(before, list) and isinstance(after, list):
        for i in range(max(len(before), len(after))):
            _walk(before[i] if i < len(before) else _ABSENT, after[i] if i < len(after) else _ABSENT,
                  path + (i,), out)
    elif before != after or type(before) is not type(after):
        out.append((path, before, after))


def _step_alone(doc: dict) -> bool:
    """`check_corpus_r16.py`'s `_step_alone`: the founder's Commitment list is one item, the step."""
    items = (((doc.get("founder_calibration") or {}).get(COMMITMENT) or {}).get("answer") or {}).get("items") or []
    return len(items) == 1


def _pairs(before: str = "r18"):
    """Each canon entry beside its record mirror (`corpus-<before>/`, `backtest-<before>/`)."""
    out = []
    for directory, mirror, backtest in ((corpus_mod.corpus_dir(KEEL_CLOUD), MIRROR / f"corpus-{before}", False),
                                        (corpus_mod.backtest_dir(KEEL_CLOUD), MIRROR / f"backtest-{before}", True)):
        for path in sorted(directory.glob("*.yaml")) if directory.is_dir() else []:
            out.append((path, mirror / path.name, backtest))
    return out


def _record_pairs(before: str, after: str):
    """Mirror against mirror: each entry's `<kind>-<after>/` record beside its `<kind>-<before>/` record."""
    return [(MIRROR / f"{'backtest' if backtest else 'corpus'}-{after}" / path.name, before_path, backtest)
            for path, before_path, backtest in _pairs(before)]


def _need_mirrors(*revisions: str):
    for rev in revisions or ("r18",):
        if not (MIRROR / f"corpus-{rev}").is_dir() or not (MIRROR / f"backtest-{rev}").is_dir():
            pytest.skip(f"keel-cloud at {KEEL_CLOUD} carries no revision-{rev[1:]} mirrors (corpus-{rev}/, "
                        f"backtest-{rev}/)")


def _load(path: Path) -> dict:
    return yaml.safe_load(path.read_text(encoding="utf-8"))


# ------------------------------------------------------------------------------------------------ rule D19

def test_every_entry_moves_by_exactly_159s_edits():
    """D19, the eval's own: 35 entries, each beside its revision-18 record; every difference the revision line (18 ->
    19), Relative advantage's row (control and codes), a Relative advantage pick moved by the one rule, or on a golden
    entry the row's optionCounts added; nothing else -- 71 golden picks and 361 back-test picks."""
    _need_mirrors("r18")
    pairs = _pairs("r18")
    assert len(pairs) == 35, [p.name for p, _, _ in pairs]
    strays, picks, counts, rows = [], {}, {}, {}
    for path, before_path, backtest in pairs:
        after, before = _load(path), _load(before_path)
        out: list = []
        _walk(before, after, (), out)
        entry = after["id"]
        for p, old, new in out:
            if p == ("revision",):
                assert (old, new) == (18, 19), (entry, old, new)
            elif p == R19_ROW + ("control",):
                assert (old, new) == ("benefit_with_advantages", "scale_four"), (entry, old, new)
                rows.setdefault(entry, set()).add("control")
            elif p[:3] == R19_ROW + ("codes",) and len(p) == 4:
                rows.setdefault(entry, set()).add("codes")
            elif len(p) == 4 and p[0] == "answers" and isinstance(p[1], int) and p[2:] == ("picks", RA):
                assert isinstance(old, dict) and "chip" not in old and new == registry_mod.from_three(old), \
                    (entry, p, old, new)
                picks.setdefault(entry, []).append(new)
            elif not backtest and p == ("expected", "standings", RA, "optionCounts"):
                assert old is _ABSENT and isinstance(new, str), (entry, old, new)
                counts[entry] = new
            else:
                strays.append((entry, p, old, new))
        assert after["respondent_questions"][RA]["codes"] == R19_CODES, entry
        assert before["respondent_questions"][RA]["codes"] == ["positive", "neutral", "negative"], entry
        # every chip as it was: a person's escape is the same object both sides
        for a, b in zip(before.get("answers") or [], after.get("answers") or []):
            was = (a.get("picks") or {}).get(RA)
            if isinstance(was, dict) and "chip" in was:
                assert (b.get("picks") or {}).get(RA) == was, (entry, a["person"])
    assert not strays, strays
    assert rows == {e: {"control", "codes"} for e in rows} and len(rows) == 35
    golden = {path.stem for path, _, backtest in pairs if not backtest}
    assert {e: len(v) for e, v in picks.items() if e in golden} == R19_GOLDEN_PICKS
    moved = [code for e, v in picks.items() if e not in golden for code in v]
    assert {code: moved.count(code) for code in R19_CODES} == R19_BACKTEST_PICKS and len(moved) == 361
    assert set(counts) == golden


def test_revision_19_moves_no_standing_and_the_scale_counts_are_the_people_inside_and_outside():
    """159 T016: no standing, drift, inside, n, median or verdict moved -- every entry's `expected` is revision 18's
    whole but the golden Relative advantage row's optionCounts -- and those counts are the four's: a lot better plus a
    little better is the row's inside, no difference plus worse its outside; a little better is 0 on every golden row
    (every recorded *better* carried a benefit)."""
    _need_mirrors("r18")
    for path, before_path, backtest in _pairs("r18"):
        after, before = _load(path), _load(before_path)
        got = after.get("expected")
        if not backtest:
            row = dict(got["standings"][RA])
            option_counts = row.pop("optionCounts")
            got = {**got, "standings": {**got["standings"], RA: row}}
            numbers = dict((k.strip(), int(v)) for k, v in (pair.split("=") for pair in option_counts.split(",")))
            assert list(numbers) == R19_CODES, (after["id"], option_counts)
            assert tuple(numbers.values()) == R19_OPTION_COUNTS[after["id"]], (after["id"], option_counts)
            assert numbers["a_lot_better"] + numbers["a_little_better"] == row["inside"], after["id"]
            assert numbers["no_difference"] + numbers["worse"] == row["outside"], after["id"]
        assert got == before.get("expected"), after["id"]
        for person in after.get("answers") or []:
            pick = (person.get("picks") or {}).get(RA)
            assert pick is None or pick in R19_CODES or (isinstance(pick, dict) and set(pick) == {"chip"}), \
                (after["id"], person["person"], pick)


# ----------------------------------------------------------------------------- rule D18, the record (spec 086)

def test_revision_18_moved_exactly_152s_edits_on_the_record():
    """D18 kept as the record (spec 086 FR-2), mirror against mirror: `corpus-r18/` and `backtest-r18/` beside
    `corpus-r17/` and `backtest-r17/`; 35 entries, each beside its revision-17 record; every difference the revision
    line (17 ->
    18), on a golden entry one of the eight belief fields 152's templates move (all eight moved, strings both sides),
    on a back-test entry the rate cost's belief sentence (on exactly the eleven rate entries); nothing else."""
    _need_mirrors("r17", "r18")
    pairs = _record_pairs("r17", "r18")
    assert len(pairs) == 35, [p.name for p, _, _ in pairs]
    counts, strays, moved = {}, [], {}
    for path, before_path, backtest in pairs:
        after, before = _load(path), _load(before_path)
        out: list = []
        _walk(before, after, (), out)
        counts[after["id"]] = len(out)
        fields = R18_BACKTEST if backtest else R18_GOLDEN
        for p, old, new in out:
            if p == ("revision",):
                assert (old, new) == (17, 18), (after["id"], old, new)
            elif (len(p) == 3 and p[0] == "founder_calibration" and (p[1], p[2]) in fields
                  and isinstance(old, str) and isinstance(new, str)):
                moved.setdefault(after["id"], set()).add((p[1], p[2]))
            else:
                strays.append((after["id"], p, old, new))
    assert not strays, strays
    golden = {path.stem for path, _, backtest in pairs if not backtest}
    assert len(golden) == 7
    assert {e: f for e, f in moved.items() if e in golden} == {e: R18_GOLDEN for e in golden}
    assert {e for e in moved if e not in golden} == R18_RATE_ENTRIES
    assert counts == {e: 1 + (len(R18_GOLDEN) if e in golden else len(R18_BACKTEST) if e in R18_RATE_ENTRIES else 0)
                      for e in counts}
    assert sum(counts.values()) == 35 + 56 + 11


def test_revision_18_moved_no_standing_and_wrote_the_new_words_on_the_record():
    """D18's second half, kept as the record (mirror against mirror) -- 152 T008: no standing, drift, inside, n, median or verdict moved -- every entry's `expected` is revision 17's,
    whole -- and the moved words are the templates': Prevalence's phrase one of the five shares and the sentence opening
    on it, Relative advantage's phrase *given them* + the benefit, Commitment *Most ... would ... now.*, Current solution
    *For most ..., ... still falls short.*, Compatibility *For most, ...*, Importance *Of these ...*; and the eleven rate
    costs *The problem already costs the payer about ...: ...*."""
    _need_mirrors("r17", "r18")
    for path, before_path, backtest in _record_pairs("r17", "r18"):
        after, before = _load(path), _load(before_path)
        assert after.get("expected") == before.get("expected"), after["id"]
        cal = after.get("founder_calibration") or {}
        if backtest:
            if after["id"] in R18_RATE_ENTRIES:
                said = cal["commercial.existing_sacrifice"]["belief_sentence"]
                assert said.startswith("The problem already costs the payer about ") and ": " in said, said
            continue
        phrase = cal["problem.prevalence"]["belief_phrase"]
        assert phrase in R18_PREVALENCE, (after["id"], phrase)
        assert cal["problem.prevalence"]["belief_sentence"].startswith(phrase + " of these "), after["id"]
        assert cal["solution.relative_advantage"]["belief_phrase"].startswith("given them "), after["id"]
        ra = cal["solution.relative_advantage"]["belief_sentence"]
        assert ra.startswith("For most, it would have given them ") and " on their last " in ra, ra
        assert cal["commercial.commitment"]["belief_sentence"].startswith("Most ") and \
            cal["commercial.commitment"]["belief_sentence"].endswith(" now."), after["id"]
        assert cal["problem.current_solution_satisfaction"]["belief_sentence"].endswith(" still falls short."), \
            after["id"]
        assert cal["solution.compatibility"]["belief_sentence"].startswith("For most, "), after["id"]
        assert cal["problem.importance"]["belief_sentence"].startswith("Of these "), after["id"]


# ------------------------------------------------------------------------------ rule D17, the record (spec 080)

def test_revision_17_moved_exactly_147s_edits_on_the_record():
    """D17 kept as the record (spec 080 FR-2), mirror against mirror: `corpus-r17/` and `backtest-r17/` beside
    `corpus-r16/` and `backtest-r16/` -- every difference the revision line (16 -> 17) or, on 02-compliancelog alone,
    one of the Buyer and payer row's four fields as 147 moved it; the row's n and option counts and every entry's
    `expected` other than its standings revision 16's."""
    _need_mirrors("r16", "r17")
    pairs = _record_pairs("r16", "r17")
    assert len(pairs) == 35
    counts, strays, row = {}, [], {}
    for r17_path, before_path, backtest in pairs:
        after, before = _load(r17_path), _load(before_path)
        out: list = []
        _walk(before, after, (), out)
        counts[after["id"]] = len(out)
        for p, old, new in out:
            if p == ("revision",):
                assert (old, new) == (16, 17), (after["id"], old, new)
            elif (not backtest and after["id"] == R17_ENTRY and len(p) == 4 and p[:3] == R17_ROW
                  and R17_FIELDS.get(p[3]) == (old, new)):
                row[p[3]] = (old, new)
            else:
                strays.append((after["id"], p, old, new))
        assert {k: v for k, v in (after.get("expected") or {}).items() if k != "standings"} == \
            {k: v for k, v in (before.get("expected") or {}).items() if k != "standings"}, after["id"]
    assert not strays, strays
    assert row == R17_FIELDS
    assert counts == {entry: 1 + (len(R17_FIELDS) if entry == R17_ENTRY else 0) for entry in counts}
    got = _load(MIRROR / "corpus-r17" / f"{R17_ENTRY}.yaml")["expected"]["standings"]["commercial.buyer_payer_alignment"]
    was = _load(MIRROR / "corpus-r16" / f"{R17_ENTRY}.yaml")["expected"]["standings"]["commercial.buyer_payer_alignment"]
    assert (got["n"], got["optionCounts"]) == (was["n"], was["optionCounts"]) and got["n"] == 9


# ----------------------------------------------------------------------------- rule D16, the record (spec 068)

def test_revision_16_moved_exactly_129s_edits_on_the_record():
    """D16 kept as the record (spec 068 FR-1), mirror against mirror: `corpus-r16/` and `backtest-r16/` beside
    `corpus-r15/` and `backtest-r15/` -- every difference the revision line (15 -> 16) or a step-alone back-test
    entry's `yes_after_trying` moved to `yes_start`, the picks per entry 129's listing (112), the golden seven by their
    revision line alone."""
    _need_mirrors("r15", "r16")
    assert sum(MOVED_PICKS.values()) == 112 and len(MOVED_PICKS) == 28
    counts, moved, strays = {}, {}, []
    pairs = _record_pairs("r15", "r16")
    assert len(pairs) == 35
    for r16_path, before_path, backtest in pairs:
        after, before = _load(r16_path), _load(before_path)
        out: list = []
        _walk(before, after, (), out)
        counts[after["id"]] = len(out)
        for p, old, new in out:
            if p == ("revision",):
                assert (old, new) == (15, 16), (after["id"], old, new)
            elif (backtest and _step_alone(before) and len(p) == 4 and p[0] == "answers" and isinstance(p[1], int)
                  and p[2:4] == ("picks", COMMITMENT)):
                assert (old, new) == ("yes_after_trying", "yes_start"), (after["id"], p, old, new)
                moved.setdefault(after["id"], set()).add(after["answers"][p[1]]["person"])
            else:
                strays.append((after["id"], p, old, new))
        if backtest:
            was = {a["person"] for a in before.get("answers") or []
                   if (a.get("picks") or {}).get(COMMITMENT) == "yes_after_trying"}
            assert moved.get(after["id"], set()) == was, (after["id"], was)
    assert not strays, strays
    assert {k: len(v) for k, v in moved.items()} == MOVED_PICKS
    assert moved["11-issen"] == ISSEN_SEVEN
    assert counts == {entry: 1 + MOVED_PICKS.get(entry, 0) for entry in counts}


def test_no_golden_entry_answers_yes_after_trying_without_the_smaller_step():
    """129 FR-12 / r14 rule T: the golden seven's second yes sits only where the founder's list carries the smaller
    step (02, 03, 06) -- at revision 19 as at 16, 17 and 18."""
    for path in sorted(corpus_mod.corpus_dir(KEEL_CLOUD).glob("*.yaml")):
        doc = _load(path)
        trying = [a["person"] for a in doc.get("answers") or []
                  if (a.get("picks") or {}).get(COMMITMENT) == "yes_after_trying"]
        assert not trying or not _step_alone(doc), (doc["id"], trying)


def test_the_cloud_checker_prints_ok_on_every_entry():
    """`check_corpus_r19.py` itself (the cloud's D19 and RA19 on the scale, RC both ways and Q, with every older rule --
    r18's B, P18 and C) over the 35 entries."""
    _need_mirrors("r18")
    if not SIM.is_file():
        pytest.skip(f"keel-cloud at {KEEL_CLOUD} carries no {SIM.name}")
    failed = {}
    pairs = _pairs("r18")
    assert len(pairs) == 35
    for path, _, _ in pairs:
        run = subprocess.run([sys.executable, "-I", str(SIM), str(path)], cwd=SIM.parent, capture_output=True,
                             text=True, timeout=120)
        last = (run.stdout.strip().splitlines() or [""])[-1]
        if run.returncode != 0 or not last.startswith("OK "):
            failed[path.name] = run.stdout[-800:] + run.stderr[-400:]
    assert not failed, failed


def test_every_revision_19_entry_loads_in_its_mode_and_a_revision_18_file_is_refused_by_name(tmp_path):
    """Every one of the 35 loads at 19 (the 28 in back-test mode); r18's 03-lullaby is refused by name."""
    _need_mirrors("r18")
    for path, _, backtest in _pairs("r18"):
        entry = corpus_mod.load_file(path, registry=fx.registry(), backtest=backtest)
        assert entry.revision == 19, entry.id
    raw = _load(MIRROR / "corpus-r18" / "03-lullaby.yaml")
    with pytest.raises(corpus_mod.CorpusError, match="revision is 18; this eval reads revision 19 only -- revision 18 "
                                                     "is MARKS_VERSION 21's corpus before keel-cloud 159"):
        corpus_mod.load_file(fx.write_entry(tmp_path, raw, name="03-lullaby.yaml"), registry=fx.registry())


# ------------------------------------------------------------------------------------------------- rule Q

def _issen_raw() -> dict:
    path = corpus_mod.backtest_dir(KEEL_CLOUD) / "11-issen.yaml"
    if not path.is_file():
        pytest.skip(f"no 11-issen at {path.parent}")
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def _refused(tmp_path, raw) -> str:
    path = fx.write_entry(tmp_path, raw, name=f"{raw['id']}.yaml")
    with pytest.raises(corpus_mod.CorpusError) as refused:
        corpus_mod.load_file(path, registry=fx.registry(), backtest=True)
    return str(refused.value)


def test_the_condition_is_read_per_person_and_no_is_outside_the_segment():
    path = corpus_mod.backtest_dir(KEEL_CLOUD) / "11-issen.yaml"
    if not path.is_file():
        pytest.skip(f"no 11-issen at {path.parent}")
    entry = corpus_mod.load_file(path, registry=fx.registry(), backtest=True)
    outside = [p.person for p in entry.people() if not p.in_segment]
    assert outside == ["Nikos Ferrante"]
    assert {p.condition for p in entry.people() if p.link == corpus_mod.LINK_PRIMARY} == {"YES", "NO"}
    nikos = next(p for p in vs.person_inputs(entry) if p.person == "Nikos Ferrante")
    assert nikos.in_segment is False and nikos.picks == [] and nikos.response("t") == {"outsideSegment": True,
                                                                                      "answers": []}


def test_a_condition_answer_is_yes_or_no_on_the_primary_link_where_the_context_records_one(tmp_path):
    raw = _issen_raw()
    bad = dict(raw, answers=[dict(raw["answers"][0], condition="MOSTLY")] + raw["answers"][1:])
    assert "condition 'MOSTLY' is not YES or NO (rule Q)" in _refused(tmp_path, bad)
    bare = dict(raw, context={k: v for k, v in raw["context"].items() if k != "condition"})
    assert "where the context records no condition (rule Q)" in _refused(tmp_path, bare)
    both = dict(raw, answers=[dict(raw["answers"][0], condition="NO", in_segment=True)] + raw["answers"][1:])
    assert "in_segment True disagrees with condition 'NO'" in _refused(tmp_path, both)


def test_a_condition_on_the_decision_makers_link_is_refused(tmp_path):
    raw = fx.raw_entry(fx.ENTRY_B2B)
    raw.pop("expected", None)
    raw.update(id="97-cond", idea_name="Whistle key tag", sources="97-cond.sources.md")
    raw["context"] = dict(raw["context"], condition="keep keys on a hook")
    decider = next(i for i, p in enumerate(raw["answers"]) if p.get("link") == corpus_mod.LINK_B2B)
    raw["answers"][decider] = dict(raw["answers"][decider], condition="YES")
    assert "the condition chip is asked on the primary link only (rule Q)" in _refused(tmp_path, raw)


def test_transloads_two_managers_opt_in_to_the_pilot():
    path = corpus_mod.backtest_dir(KEEL_CLOUD) / "12-transload.yaml"
    if not path.is_file():
        pytest.skip("no 12-transload")
    entry = corpus_mod.load_file(path, registry=fx.registry(), backtest=True)
    opted = {p.person for p in vs.person_inputs(entry) if p.pilot_opt_in}
    assert PILOTS["12-transload"] <= opted, opted


def test_a_person_outside_is_walked_inside_where_the_page_serves_no_chip():
    """FR-6: Keel's AI writes the gate's segment chip (keel-cloud 120 FR-2); where it writes none, Nikos Ferrante (NO) is
    walked on his recorded gate answer, story and picks (`vs.inside_inputs`), and the journey names it."""
    path = corpus_mod.backtest_dir(KEEL_CLOUD) / "11-issen.yaml"
    if not path.is_file():
        pytest.skip(f"no 11-issen at {path.parent}")
    entry = corpus_mod.load_file(path, registry=fx.registry(), backtest=True)
    nikos = vs.inside_inputs(entry, "Nikos Ferrante")
    assert nikos.in_segment and nikos.recency is True and nikos.picks and nikos.story
    assert nikos.response("t")["recency"] is True


# ------------------------------------------------------------------------------- FR-1: the Answer box at load

def test_every_entry_fits_the_answer_box_and_revision_14s_transload_stops_at_load(tmp_path):
    """Spec 067 FR-1 (keel-cloud 128 FR-17, FR-20): all 35 revision-19 entries name every Importance item inside the
    25-word Answer; revision 14's 12-transload (*Running the shift with too few workers*) did not, and the harness
    then lost *Finding freight sitting at the wrong door* -- read at revision 15, it stops at load naming the label."""
    _need_mirrors()
    for path, _, backtest in _pairs():
        vs.check_answer_box(corpus_mod.load_file(path, registry=fx.registry(), backtest=backtest))
    if not (MIRROR / "backtest-r14").is_dir():
        pytest.skip(f"keel-cloud at {KEEL_CLOUD} carries no revision-14 back-test mirror")
    raw = yaml.safe_load((MIRROR / "backtest-r14" / "12-transload.yaml").read_text(encoding="utf-8"))
    raw["revision"] = corpus_mod.REVISION
    # spec 086: revision 18's rate cost belief (keel-cloud 152, rule C) -- the record's own words, so the read reaches
    # the Answer box rather than stopping on revision 14's *Most dock supervisors ... lose about ...*
    now = _load(corpus_mod.backtest_dir(KEEL_CLOUD) / "12-transload.yaml")
    raw["founder_calibration"]["commercial.existing_sacrifice"]["belief_sentence"] = \
        now["founder_calibration"]["commercial.existing_sacrifice"]["belief_sentence"]
    # spec 089: revision 19's scale (keel-cloud 159, rule RA19) -- the row and every pick by the one rule, as the record
    raw["respondent_questions"][RA] = now["respondent_questions"][RA]
    for person in raw.get("answers") or []:
        if RA in (person.get("picks") or {}):
            person["picks"][RA] = registry_mod.from_three(person["picks"][RA])
    entry = corpus_mod.load_file(fx.write_entry(tmp_path, raw, name="12-transload.yaml"), registry=fx.registry(),
                                 backtest=True)
    with pytest.raises(vs.VectorsScriptError) as stopped:
        vs.founder_inputs(entry)
    assert "'Finding freight sitting at the wrong door' would be dropped" in str(stopped.value), str(stopped.value)
    assert vs.answer_drops(entry, "problem.importance") == ["Finding freight sitting at the wrong door"]


def test_a_list_label_past_the_answer_box_stops_at_load(tmp_path):
    """Bound to the registry a label is held to its `saves.max_words` (nine) first; read unbound, the harness's own
    stop names it."""
    raw = fx.raw_entry(fx.ENTRY)
    items = raw["founder_calibration"]["problem.importance"]["answer"]["items"]
    items[1]["label"] = " ".join(["word"] * 26)
    entry = corpus_mod.load_file(fx.write_entry(tmp_path, raw))
    with pytest.raises(vs.VectorsScriptError, match="is 26 words; the Answer box takes 25"):
        vs.check_answer_box(entry)


# ------------------------------------------------------------------------------- FR-2: every founder rung typed

def test_the_rungs_the_draft_left_out_are_typed_and_past_the_screen_they_stop():
    """Spec 067 FR-2 (keel-cloud 128 FR-16): 16-pairio's founder has five rungs; the Answer's 25 words carry the first
    few and Keel's draft carries what it was given -- a redrafted row is typed over (the rows are positional), a rung
    past the drawn rows is typed into a new row, in the entry's order; past the screen's rows the walk stops naming
    the rung."""
    path = corpus_mod.backtest_dir(KEEL_CLOUD) / "16-pairio.yaml"
    if not path.is_file():
        pytest.skip("no 16-pairio")
    entry = corpus_mod.load_file(path, registry=fx.registry(), backtest=True)
    rungs = [i["label"] for i in vs.founder_list(entry, "problem.current_solution_satisfaction")["items"]]
    assert len(rungs) == 5
    drawn = [rungs[0], rungs[1].upper() + "."]                       # case and a full stop are no difference
    assert vs.rungs_plan(entry, drawn, 5) == {"edit": [], "add": rungs[2:], "cannot": []}
    # Keel redrafted the third row (Karsa, 2026-10-23): typed over, not added
    assert vs.rungs_plan(entry, drawn + ["Keel's own rung"], 5) == {"edit": [(2, rungs[2])], "add": rungs[3:],
                                                                   "cannot": []}
    assert vs.rungs_plan(entry, rungs, 5) == {"edit": [], "add": [], "cannot": []}
    # a screen of four rows cannot hold the fifth rung
    assert vs.rungs_plan(entry, rungs[:4], 4) == {"edit": [], "add": [], "cannot": [rungs[4]]}


# ------------------------------------------------------------------------------- FR-3: a line belongs to a rung

def _with_follow_up(value) -> dict:
    raw = fx.raw_entry(fx.ENTRY_B2B)
    raw.pop("expected", None)
    raw.update(id="96-rung", idea_name="Whistle key tag", sources="96-rung.sources.md")
    who = next(i for i, p in enumerate(raw["answers"]) if p.get("recency") == "yes")
    raw["answers"][who] = dict(raw["answers"][who], follow_up=value)
    return raw, raw["answers"][who]["person"]


def test_a_follow_up_names_its_rung_and_the_reader_keeps_it(tmp_path):
    raw, who = _with_follow_up({"dimension": "commercial.commitment", "text": "We'd start with one site first."})
    entry = corpus_mod.load_file(fx.write_entry(tmp_path, raw, name="96-rung.yaml"), registry=fx.registry(),
                                 backtest=True)
    person = entry.person(who)
    assert (person.follow_up, person.follow_up_dimension) == ("We'd start with one site first.", "commercial.commitment")
    inputs = next(p for p in vs.person_inputs(entry) if p.person == who)
    assert inputs.follow_up_dimension == "commercial.commitment"
    # a bare line is still read at revision 15 (judgement call 3): no rung
    raw, who = _with_follow_up("A bare line, as every r15 entry writes it.")
    entry = corpus_mod.load_file(fx.write_entry(tmp_path, raw, name="96-rung.yaml"), registry=fx.registry(),
                                 backtest=True)
    assert entry.person(who).follow_up_dimension is None and entry.person(who).follow_up


@pytest.mark.parametrize("value, why", [
    ({"dimension": "problem.frequency", "text": "Twice a week."}, "which is asked no follow-up"),
    ({"dimension": "commercial.commitment", "text": "  "}, "carries no words"),
    ({"dimension": "commercial.commitment"}, "it is {dimension, text}"),
    (["a list"], "it is {dimension, text}"),
])
def test_a_follow_up_off_its_shape_is_refused(tmp_path, value, why):
    raw, _ = _with_follow_up(value)
    assert why in _refused(tmp_path, raw)


# ------------------------------------------------------------------------------- FR-4: the served bar

def test_current_solution_is_counted_against_by_the_served_line():
    """Spec 067 FR-4 (keel-cloud 117 FR-3 / 128 FR-16, Pairio's Walter): with the served line at 1 only `outcome_1` is
    against; the registry's `outcome_1, outcome_2` stand only where no line is served (D4's 2, every golden entry)."""
    from harness import interviewer_fake as fake                       # noqa: PLC0415
    walter = {"dimension": "problem.current_solution_satisfaction", "codes": ["outcome_2"], "chip": None}
    key = "problem.current_solution_satisfaction"
    assert fake.against(key, walter, fake.Founder()) is True
    assert fake.against(key, walter, fake.Founder(current_line=1)) is False
    assert fake.against(key, dict(walter, codes=["outcome_1"]), fake.Founder(current_line=1)) is True
    assert fake.against(key, dict(walter, codes=["outcome_3"]), fake.Founder(current_line=3)) is True
    assert fake.against(key, dict(walter, codes=["outcome_4"]), fake.Founder(current_line=3)) is False


def test_a_two_step_price_below_on_either_step_is_against():
    """keel-cloud 128 FR-21 (`Ladder.against`, AirCaps's Diego and Amaka): up front then a plan, held on both steps."""
    from harness import interviewer_fake as fake                       # noqa: PLC0415
    founder = fake.Founder(price_low=20.0, upfront_low=100.0, chain_price=True)
    pick = lambda *codes: {"dimension": "commercial.price", "codes": list(codes), "chip": None}  # noqa: E731
    assert fake.against("commercial.price", pick("upfront.band_50_100", "band_20_50"), founder) is True
    assert fake.against("commercial.price", pick("upfront.band_100_250", "band_10_20"), founder) is True
    assert fake.against("commercial.price", pick("upfront.band_100_250", "band_20_50"), founder) is False


def test_the_composer_says_a_fact_back_as_the_fact_and_quotes_worse():
    """keel-cloud 128 FR-13b / FR-16 (`FollowUpComposer`): a fact answered No reads *You said no to this: {the fact}.
    What got in the way?* and is said as it reads; Relative advantage's worse is quoted."""
    assert vs.fact_said("Their phone was within reach of the cot.") == "your phone was within reach of the cot"
    assert vs.from_served("Think of your last shift. Did the list come straight out of the EMR?", "No") == \
        "You said no to this: did the list come straight out of the EMR? What got in the way?"
    assert vs.served_idea_name({"reveal": {"what": "Imagine Pairio."}}) == "Pairio"


# ------------------------------------------------------------------------------- FR-5: needs-input answered once

def _asking_journey(view: dict, *, strict: bool = False):
    from types import SimpleNamespace                                   # noqa: PLC0415
    path = corpus_mod.backtest_dir(KEEL_CLOUD) / "20-lemma.yaml"
    if not path.is_file():
        pytest.skip("no 20-lemma")
    entry = corpus_mod.load_file(path, registry=fx.registry(), backtest=True)
    posted = []
    j = SimpleNamespace(strict=strict, entry=entry, founder=vs.founder_inputs(entry), findings=[], posted=posted,
                        get=lambda path: view,
                        call=lambda method, path, body=None, ok=(): posted.append((method, path, body)) or (201, {}))
    return j


def test_a_needs_input_is_answered_once_from_the_entrys_fields_and_a_second_ask_stops(monkeypatch):
    """Spec 067 FR-5 (keel-cloud 128 FR-15, Lemma): AWAITING_INPUT is answered once with the entry's own words, the
    question a finding; asked again it stops at once, never a 660 s wait; a golden walk stops at the first ask."""
    import contextlib                                                   # noqa: PLC0415
    from types import SimpleNamespace                                   # noqa: PLC0415
    from evals import corpus_scenario as cs                             # noqa: PLC0415
    monkeypatch.setattr(cs, "_step", lambda *a, **k: contextlib.nullcontext(SimpleNamespace(
        record_wire=lambda *x: None)))
    view = {"status": "AWAITING_INPUT", "turns": [{"turnNumber": 1}],
            "questions": [{"id": "q1", "question": "In your own words: who has this problem?"}]}
    j = _asking_journey(view)
    asked: dict = {}
    cs._needs_input(j, "iid", asked)
    assert len(j.posted) == 1 and j.posted[0][1] == "/v2/inference-interactions/iid/answers"
    content = j.posted[0][2]["content"]
    assert j.founder.context_fields["actor"] in content and j.founder.context_fields["segment"] in content
    assert j.findings and "answered once" in j.findings[0]["what"]
    cs._needs_input(j, "iid", asked)                                    # the same turn, still on its way: nothing
    assert len(j.posted) == 1
    view["turns"].append({"turnNumber": 2})                             # asked again
    with pytest.raises(AssertionError, match="asked the founder back again"):
        cs._needs_input(j, "iid", asked)
    with pytest.raises(AssertionError, match="spec 067 FR-5"):
        cs._needs_input(_asking_journey(dict(view), strict=True), "iid", {})
    quiet = _asking_journey({"status": "PENDING"})
    cs._needs_input(quiet, "iid", {})
    cs._needs_input(quiet, None, {})
    assert not quiet.posted and not quiet.findings


# ------------------------------------------------------------------------------- FR-8: the spoken guard

def test_the_backtest_record_holds_every_served_item_to_the_spoken_form():
    """Spec 067 FR-8 (keel-cloud 128 FR-10): each served item, as the page fetched it, read back through S1-S10 with its
    stem's length; keel-cloud's own composed Lullaby items are clean, and a 21-word stem is a red line, not a note."""
    from types import SimpleNamespace                                   # noqa: PLC0415
    from evals import backtest as bt                                    # noqa: PLC0415
    from instructions import cloud_corpus as cloud_mod                  # noqa: PLC0415
    try:
        registry = cloud_mod.registry_of_record(KEEL_CLOUD)
        corpus = corpus_mod.load(KEEL_CLOUD).bind(registry)
        cloud = cloud_mod.read(KEEL_CLOUD, corpus=corpus, registry=registry)
    except Exception as missing:                                        # noqa: BLE001
        pytest.skip(f"no keel-cloud record: {missing}")
    lullaby = corpus.by_id("03-lullaby")
    items = cloud.items_of("03-lullaby")

    def served(ci, stem=None):
        return {"dimension": ci.key, "question": ci.question if stem is None else stem,
                "options": [{"optionId": str(n), "label": o} for n, o in enumerate(ci.options)],
                "escape": {"code": "X", "label": ci.escape} if ci.escape else None,
                "spoken": {"anchor": ci.anchor, "stem": ci.stem if stem is None else stem, "countLine": ci.count_line,
                           "optionsLine": ci.options_line, "escapeLine": ci.escape_line, "transform": ci.transform}}
    long = " ".join(["word"] * 20) + " too?"
    interview = {"kind": "FULL", "parts": [{"part": 1, "items": [served(ci) for ci in items]
                                            + [dict(served(items[0], stem=long), dimension=items[0].key)]}]}
    j = SimpleNamespace(entry=lullaby, registry=registry, interviews={"Amira Saleh": interview, "Twin": interview})
    guard = bt.spoken_guard(j)
    assert guard["items"] == len(items) + 1                             # the second person's same words are one row
    assert guard["clean"] == len(items) and guard["longest_stem"] == 21
    red = guard["red"][0]
    assert red["stem_words"] == 21 and any(f.startswith("S1") for f in red["faults"])
    md = bt.markdown({"spoken_guard": guard, "respondents": {}, "founder_screens": []})
    assert "**RED**" in md and f"{len(items)} of {len(items) + 1} items clean" in md


# ------------------------------------------------------------------------------- FR-7: the changed screens, read

def test_the_changed_screens_are_read_as_findings_on_a_back_test():
    """Spec 067 FR-7 (judgement call 6): a consumer link saying *per person*, a plan drawn after *I wouldn't pay for
    this*, *People disagree* on a bar line -- each recorded; a B2B study's own words are not consumer words."""
    from types import SimpleNamespace                                   # noqa: PLC0415
    from evals import backtest as bt                                    # noqa: PLC0415
    path = corpus_mod.backtest_dir(KEEL_CLOUD) / "13-aircaps.yaml"
    if not path.is_file():
        pytest.skip("no 13-aircaps")
    entry = corpus_mod.load_file(path, registry=fx.registry(), backtest=True)
    andrea = next(p.person for p in entry.people() if (p.picks or {}).get("commercial.price")
                  and bt._closed_price(p.picks["commercial.price"]) and isinstance(p.picks["commercial.price"], list))
    assert andrea == "Andrea Whitlock"
    interview = {"kind": "FULL", "parts": [{"part": 3, "items": [
        {"dimension": "commercial.price", "question": "What would AirCaps be worth to you a month, per person?",
         "options": [{"optionId": "o", "label": "Under $10"}]}]}]}
    standings = {"facts": {"cards": [{"key": "solution.compatibility", "number": "3 of 7",
                                      "statusWords": "People disagree"},
                                     {"key": "problem.importance", "number": "4 of 7",
                                      "statusWords": "People disagree"}]}}
    walked = {andrea: {"screens": [{"dimension": "commercial.price", "plan": {"question": "And after that ..."}}]}}
    j = SimpleNamespace(entry=entry, interviews={andrea: interview}, walked=walked)
    got = bt.changed_screens(j, standings)
    assert [r["word"] for r in got["consumer_words"]] == ["per person"]
    assert [r["person"] for r in got["plan_after_closed_price"]] == [andrea]
    assert [r["key"] for r in got["people_disagree_on_a_bar_line"]] == ["solution.compatibility"]
    assert "*per person*" in bt.markdown({"changed_screens": got, "respondents": {}, "founder_screens": []})


# ------------------------------------------------------------------------------- the register's Re-run column

def test_the_rerun_row_carries_the_run_and_the_registers_last_score():
    """Spec 067 (keel-cloud 128 acceptance 4): the row a re-run adds -- read, never written -- names the run, the door,
    the decision, the score (to be judged) and the score of the entry's last row in the register."""
    from evals import backtest as bt                                    # noqa: PLC0415
    register = ("| Entry | Judged | Run | Door | Decision | Score | Zeros | What went wrong (top three) | Fixed by |\n"
                "|---|---|---|---|---|---|---|---|---|\n"
                "| 09-karsa | 2026-10-23 | 20261023T115825Z | host | BUILD_BUT_CHANGE · MEDIUM | 60% (94/156) | 11 | a | b |\n"
                "| 10-palus | 2026-10-23 | 20261023T121135Z | host | NOT_YET · MEDIUM | 60% (82/136) | 10 | c | d |\n")
    assert bt.register_scores(register, "09-karsa") == ["60% (94/156)"]
    row = {"id": "09-karsa", "run": "20261024T010000Z", "door": "host", "decision": "NOT_YET", "score": None}
    assert bt.rerun_row(row, register) == ("re-run row: | 09-karsa | (judged: to fill) | 20261024T010000Z | host | "
                                           "NOT_YET | to be judged | Re-run: after 128 · was 60% (94/156) |")
    assert bt.rerun_row(dict(row, id="11-issen"), register).endswith("was no earlier row |")
    real = bt._register_text()
    if real:                                                            # keel-cloud's own register, read as data
        assert bt.register_scores(real, "09-karsa"), "the register's Karsa row"
