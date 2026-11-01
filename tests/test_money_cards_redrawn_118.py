"""Spec 118 -- the harness reads the money cards redrawn (keel-cloud 180-183, keel-web 155), the problem and solution
cards (keel-cloud 184) and the question screens (keel-cloud 185, keel-web 156); corpus revision 21.

Against keel-cloud-docs `f3f0d99e` (contract 55, corpus revision 21; its build records of record) and keel-web
`3c0db0c`. **D20 and D21**, the eval's own diffs: the revision-19 record beside the revision-20 record (keel-cloud 181 /
182) and the revision-20 record beside canon (185), every leaf difference one of the listed edits. Then each moved
mirror, pinned with why; the two new items answered on the entries; the after-answers leg's reader on a fixture page
with and without `bar-strip`; one scripted line per follow-up. Where keel-cloud's checkout lacks a mirror the test skips
by name (judgement call 4 of spec 067's tasks.md).
"""

from __future__ import annotations

import inspect
from pathlib import Path
from types import SimpleNamespace

import pytest
import yaml
from playwright.sync_api import sync_playwright

from evals import backtest as bt
from evals import corpus_scenario as cs
from evals import interviewer_leg as il
from harness import interviewer_fake as fake
from harness import interviewer_screens as ivs
from harness import interviews_screens as iv
from harness import vectors_screens as vs_screens
from harness import vectors_script as vs
from instructions import brief_facts as bf
from instructions import chain as chain_mod
from instructions import cloud_corpus as cloud_mod
from instructions import corpus as corpus_mod
from instructions import friction as friction_mod
from instructions import spoken as spoken_mod
from quality import readers
from stack.config import load_config

KEEL_CLOUD = Path(load_config(validate=False).keel_cloud)
KEEL_WEB = Path(load_config(validate=False).keel_web)
MIRROR = KEEL_CLOUD / "src" / "test" / "resources" / "keel"
AB, PF, PRICE, CO = ("commercial.ability_to_pay", "commercial.purchase_friction", "commercial.price",
                     "solution.compatibility")
SACRIFICE = "commercial.existing_sacrifice"
_ABSENT = object()


@pytest.fixture(scope="module")
def registry():
    try:
        return cloud_mod.registry_of_record(KEEL_CLOUD)
    except Exception as missing:                                        # noqa: BLE001
        pytest.skip(f"no keel-cloud registry of record: {missing}")


def _backtest(entry_id: str, registry):
    path = corpus_mod.backtest_dir(KEEL_CLOUD) / f"{entry_id}.yaml"
    if not path.is_file():
        pytest.skip(f"no back-test entry {entry_id} at {path.parent}")
    return corpus_mod.load_file(path, registry=registry, backtest=True)


def _golden(entry_id: str, registry):
    path = corpus_mod.corpus_dir(KEEL_CLOUD) / f"{entry_id}.yaml"
    if not path.is_file():
        pytest.skip(f"no golden entry {entry_id}")
    return corpus_mod.load_file(path, registry=registry)


def _load(path: Path) -> dict:
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def _walk(before, after, path, out):
    if isinstance(before, dict) and isinstance(after, dict):
        for k in list(before) + [k for k in after if k not in before]:
            _walk(before.get(k, _ABSENT), after.get(k, _ABSENT), path + (k,), out)
    elif isinstance(before, list) and isinstance(after, list) and len(before) == len(after):
        for i, (a, b) in enumerate(zip(before, after)):
            _walk(a, b, path + (i,), out)
    elif before != after or type(before) is not type(after):
        out.append((path, before, after))


def _pairs(before: str, after: str | None):
    """Each entry's `<kind>-<before>/` record beside its `<kind>-<after>/` record (`after` None: canon)."""
    for rev in (before,) + ((after,) if after else ()):
        if not (MIRROR / f"corpus-{rev}").is_dir() or not (MIRROR / f"backtest-{rev}").is_dir():
            pytest.skip(f"keel-cloud at {KEEL_CLOUD} carries no revision-{rev[1:]} mirrors")
    out = []
    for kind, canon in (("corpus", corpus_mod.corpus_dir(KEEL_CLOUD)), ("backtest", corpus_mod.backtest_dir(KEEL_CLOUD))):
        for path in sorted(canon.glob("*.yaml")):
            now = MIRROR / f"{kind}-{after}" / path.name if after else path
            out.append((MIRROR / f"{kind}-{before}" / path.name, now, kind == "backtest"))
    return out


# ------------------------------------------------------------------------------------------- rule D20

#: keel-cloud 181 / 182 (`CorpusRevisionTwentyTest`): the founder fields revision 20 moves -- the chain's three beliefs
#: (and Ability to pay's phrase), Purchase friction's belief.
D20_FOUNDER = {(SACRIFICE, "belief_sentence"), (PRICE, "belief_sentence"), (AB, "belief_sentence"),
               (AB, "belief_phrase"), (PF, "belief_sentence")}
#: keel-cloud 182 T020: the three entries the spec gives a founder's time, and the time.
TIMED = {"08-fresco": {"count": 2, "unit": "WEEKS"}, "10-palus": {"count": 4, "unit": "WEEKS"},
         "17-expanse": {"count": 6, "unit": "WEEKS"}}
#: keel-cloud 181 FR-8 / 182 T020: who keeps an Ability to pay pick on the four entries (the rest were deleted).
AB_KEPT = {"08-fresco": {"Gordon Achebe"}, "10-palus": {"Maya Feldman"},
           "17-expanse": {"Gregory Lindqvist", "Nadia Kowalski", "Arjun Mehta", "Marco Bianchi"},
           "13-aircaps": {"Shirin Tehrani"}}


def _one_rule(code, founder):
    """182 T020's one rule: `yes_quick` -> the band just under the founder's time, `yes_long` -> the band from it."""
    bands = friction_mod.bands(friction_mod.Duration.of(founder))
    under = next(c for c, lo, hi, _ in bands if hi == friction_mod.Duration.of(founder).days())
    from_ = next(c for c, lo, hi, _ in bands if lo == friction_mod.Duration.of(founder).days())
    return {"yes_quick": under, "yes_long": from_}.get(code, code)


def test_revision_20_moves_exactly_181s_and_182s_edits_on_the_record():
    """D20, mirror against mirror: 35 entries; every difference the revision line (19 -> 20), one of the five belief
    fields, Ability to pay's row (the question pointing back, `cant_recall_one` -> `cant_say`), an Ability to pay pick
    deleted from a person whose Price answer is not at or above the founder's price (or a kept chip read `cant_say`),
    and on the three timed entries the founder's time, the row (`duration_bands`, the six, `cant_tell`) and each pick
    moved by the one rule -- nothing else, no standing (`expected`) anywhere."""
    pairs = _pairs("r19", "r20")
    assert len(pairs) == 35
    strays, deleted = [], {}
    for before_path, after_path, backtest in pairs:
        before, after = _load(before_path), _load(after_path)
        entry = after["id"]
        price = (after.get("founder_calibration", {}).get(PRICE) or {}).get("answer")
        out: list = []
        _walk(before, after, (), out)
        for p, old, new in out:
            if p == ("revision",):
                assert (old, new) == (19, 20), entry
            elif len(p) == 3 and p[0] == "founder_calibration" and (p[1], p[2]) in D20_FOUNDER:
                assert isinstance(new, str) and new != old, (entry, p)
            elif p == ("founder_calibration", PF, "answer", "duration"):
                assert old is _ABSENT and new == TIMED[entry], (entry, new)
            elif p == ("respondent_questions", AB, "question"):
                assert old is _ABSENT and new == chain_mod.POINTS_BACK, (entry, new)
            elif p == ("respondent_questions", AB, "escape"):
                assert (old, new) == ("cant_recall_one", "cant_say"), entry
            elif p[:2] == ("respondent_questions", PF) and entry in TIMED:
                assert p[2] in ("control", "escape", "codes"), (entry, p)
            elif len(p) == 5 and p[0] == "answers" and p[2:] == ("picks", AB, "chip"):
                # 182 T020: the one kept `cant_recall_one` chip reads `cant_say` (16-pairio)
                assert (old, new) == ("cant_recall_one", "cant_say"), (entry, p)
            elif len(p) == 4 and p[0] == "answers" and p[2:] == ("picks", AB):
                person = before["answers"][p[1]]
                if new is _ABSENT:
                    assert not chain_mod.reached(price, (person.get("picks") or {}).get(PRICE)), (entry, person)
                    deleted[entry] = deleted.get(entry, 0) + 1
                else:
                    assert (old, new) == ({"chip": "cant_recall_one"}, {"chip": "cant_say"}), (entry, p)
            elif len(p) == 4 and p[0] == "answers" and p[2:] == ("picks", PF) and entry in TIMED:
                assert new == _one_rule(old, TIMED[entry]), (entry, p, old, new)
            else:
                strays.append((entry, p, old, new))
        assert before.get("expected") == after.get("expected"), entry
    assert not strays, strays[:20]
    assert sum(deleted.values()) == 146, deleted                        # keel-cloud 182 T020: 146 people


def test_the_ability_picks_kept_at_revision_21_are_the_people_at_the_price(registry):
    """keel-cloud 181 FR-8: Fresco keeps Gordon, Palus Maya, Expanse four, AirCaps Shirin -- the reader refuses a pick
    from anyone else (`chain.reached`)."""
    for entry_id, kept in AB_KEPT.items():
        entry = _backtest(entry_id, registry)
        have = {p["person"] for p in entry.answers if AB in (p.get("picks") or {})}
        assert have == kept, (entry_id, have)
        for person in entry.answers:
            reached = chain_mod.reached(entry.price(), (person.get("picks") or {}).get(PRICE))
            assert reached == (person["person"] in kept) or PRICE not in (person.get("picks") or {}), \
                (entry_id, person["person"])


def test_a_pick_from_a_person_under_the_price_is_refused(tmp_path, registry):
    raw = _load(corpus_mod.backtest_dir(KEEL_CLOUD) / "08-fresco.yaml")
    under = next(p for p in raw["answers"] if p.get("link") == "COMMERCIAL_B2B"
                 and not chain_mod.reached(raw["founder_calibration"][PRICE]["answer"], p["picks"].get(PRICE)))
    under["picks"][AB] = "existing_line"
    path = tmp_path / "08-fresco.yaml"
    path.write_text(yaml.safe_dump(raw, sort_keys=False), encoding="utf-8")
    with pytest.raises(corpus_mod.CorpusError, match="is not at or above the founder's price"):
        corpus_mod.load_file(path, registry=registry, backtest=True)


# ------------------------------------------------------------------------------------------- rule D21

#: keel-cloud 185 T023: the 13 entries whose tested condition is a fact, and the 13 people moved only_with_help -> no.
FACT_ENTRIES = {"12-transload", "13-aircaps", "14-code-four", "17-expanse", "18-careforce", "19-veles", "20-lemma",
                "25-bidflow", "28-relvy-ai", "34-wideframe", "03-lullaby", "04-linerly", "07-mulchrun"}
DECIDERS = {"08-fresco": "Do any of your company's jobs run on Procore or ACC?",
            "10-palus": "Does your startup keep its cash with Mercury, Brex or a similar startup banking platform?",
            "17-expanse": "Does the shared SLURM or Kubernetes cluster you run have 100 or more GPUs?"}


def test_revision_21_moves_exactly_185s_edits():
    """D21, the revision-20 record beside the revision-21 record (canon until keel-cloud 187; spec 119 reads it mirror
    against mirror, `corpus-r21/` and `backtest-r21/`): the revision line (20 -> 21); on the 13 fact entries the row's
    codes the fact's three and every `only_with_help` pick `no` (13 people; on Lullaby and Mulchrun the golden row's
    counts); `screeners.decider` on the three B2B entries of the four; nothing else."""
    pairs = _pairs("r20", "r21")
    moved, strays = 0, []
    for before_path, after_path, backtest in pairs:
        before, after = _load(before_path), _load(after_path)
        entry = after["id"]
        out: list = []
        _walk(before, after, (), out)
        for p, old, new in out:
            if p == ("revision",):
                assert (old, new) == (20, 21), entry
            elif p == ("respondent_questions", CO, "codes") and entry in FACT_ENTRIES:
                assert new == list(corpus_mod.FACT_CODES) and old == ["yes_easily", "yes_with_steps",
                                                                      "only_with_help", "no"], entry
            elif len(p) == 4 and p[0] == "answers" and p[2:] == ("picks", CO):
                assert (old, new) == ("only_with_help", "no") and entry in FACT_ENTRIES, (entry, p)
                moved += 1
            elif p == ("screeners",):
                assert old is _ABSENT and new == {"decider": {"question": DECIDERS[entry], "inside": "YES"}}, entry
            elif not backtest and p == ("expected", "standings", CO, "optionCounts"):
                assert entry in ("03-lullaby", "07-mulchrun"), entry
            else:
                strays.append((entry, p, old, new))
    assert not strays, strays[:20]
    assert moved == 13


def test_every_canon_entry_loads_at_22_and_19_20_and_21_are_refused_by_name(tmp_path, registry):
    """Spec 119 re-pin (keel-cloud 187, revision 22): canon loads at 22; 19, 20 and 21 are refused by name."""
    for path in sorted(corpus_mod.corpus_dir(KEEL_CLOUD).glob("*.yaml")):
        assert corpus_mod.load_file(path, registry=registry).revision == 22
    for path in sorted(corpus_mod.backtest_dir(KEEL_CLOUD).glob("*.yaml")):
        assert corpus_mod.load_file(path, registry=registry, backtest=True).revision == 22
    for rev in ("r19", "r20", "r21"):
        record = MIRROR / f"corpus-{rev}" / "03-lullaby.yaml"
        if not record.is_file():
            pytest.skip(f"no {rev} record")
        target = tmp_path / rev
        target.mkdir()
        (target / "03-lullaby.yaml").write_text(record.read_text(encoding="utf-8"), encoding="utf-8")
        with pytest.raises(corpus_mod.CorpusError, match=f"revision is {rev[1:]}; this eval reads revision 22 only"):
            corpus_mod.load_file(target / "03-lullaby.yaml", registry=registry)


def test_a_fact_is_three_by_codes_reading_and_four_on_one_is_refused(tmp_path, registry):
    """keel-cloud 185 FR-1 (`ItemFrames.conditionKind`): the eval's `spoken.condition_kind` agrees with the cloud's on
    every entry -- the 13 facts serve three, the others (abilities, Pairio's and Paidly's permissions) four -- and a fact
    recorded on the four is refused."""
    for directory, backtest in ((corpus_mod.corpus_dir(KEEL_CLOUD), False), (corpus_mod.backtest_dir(KEEL_CLOUD), True)):
        for path in sorted(directory.glob("*.yaml")):
            entry = corpus_mod.load_file(path, registry=registry, backtest=backtest)
            tested = entry.tested(CO) or {}
            kind = spoken_mod.condition_kind(tested.get("asked"), tested.get("label"))
            assert (kind == "FACT") == (entry.id in FACT_ENTRIES), (entry.id, kind)
    raw = _load(corpus_mod.backtest_dir(KEEL_CLOUD) / "17-expanse.yaml")
    raw["respondent_questions"][CO]["codes"] = ["yes_easily", "yes_with_steps", "only_with_help", "no"]
    path = tmp_path / "17-expanse.yaml"
    path.write_text(yaml.safe_dump(raw, sort_keys=False), encoding="utf-8")
    with pytest.raises(corpus_mod.CorpusError, match="the registry's four on a fact"):
        corpus_mod.load_file(path, registry=registry, backtest=True)


# ------------------------------------------------------------- FR-1: the chain's beliefs (keel-cloud 180 / 181)

def test_the_chain_beliefs_name_who_pays(registry):
    """keel-cloud 180 FR-2 / 181 FR-4 (`CommercialChain.costBelief`, `priceBelief`, `abilityBelief`, `deciders`): the
    reader holds every chain entry's recorded words to the port (rule C); three pinned here as 180's / 181's tables say
    them. Never *the payer*, never *Keel reads*."""
    fresco, palus, aircaps = (_backtest(e, registry) for e in ("08-fresco", "10-palus", "13-aircaps"))
    cal = fresco.founder_calibration
    # spec 123 FR-1 re-pin (keel-cloud 193 FR-1, revision 22 amended in place): the hours are the superintendents'
    # (`actor_plural`), never the deciders'; *per site* is no noun of theirs, so it stays
    assert cal[SACRIFICE]["belief_sentence"] == \
        "Construction superintendents on commercial jobs already spend 30 to 60 hours per site a month on the daily log."
    assert cal[PRICE]["belief_sentence"] == "Contractor operations leads would think Fresco worth $800 to $1,000 per site a month."
    assert cal[AB]["belief_sentence"] == \
        "Contractor operations leads who would pay $800 to $1,000 per site a month could find the money for it."
    assert cal[AB]["belief_phrase"].startswith("contractors who would pay"), "the phrase reads the role, not the title"
    assert palus.founder_calibration[AB]["belief_sentence"].startswith("Startup founders who would pay the 0.25% fee")
    assert palus.founder_calibration[PRICE]["belief_sentence"] == \
        "Startup founders would think a fee of 0.25% of the balance per company a year fair for Palus."
    assert "could find it in money they already spend on this" in aircaps.founder_calibration[AB]["belief_sentence"]
    for entry in (fresco, palus, aircaps):
        said = " ".join(str(v.get("belief_sentence") or "") for v in entry.founder_calibration.values())
        assert "the payer" not in said and "Keel reads" not in said
    assert chain_mod.plural_words("head of finance") == "heads of finance" and chain_mod.plural_words("CFO") == "CFOs"
    assert chain_mod.deciders(None, "deaf adults", False) == "deaf adults"


def test_reached_reads_each_step_against_the_founders_low():
    one = {"shape": "AMOUNT_PERIOD", "low": 800, "high": 1000}
    assert chain_mod.reached(one, "band_800_2500") and chain_mod.reached(one, "over_5000")
    assert not chain_mod.reached(one, "band_500_800") and not chain_mod.reached(one, "would_not_pay")
    assert not chain_mod.reached(one, {"chip": "cant_say"}) and not chain_mod.reached(one, None)
    two = {"shape": "UPFRONT_THEN", "upfrontLow": 599, "upfrontHigh": 599, "low": 20, "high": 20}
    assert chain_mod.reached(two, ["upfront.band_599_1000", "band_20_50"])
    assert not chain_mod.reached(two, ["upfront.band_599_1000", "band_10_20"])
    assert not chain_mod.reached(two, ["upfront.band_250_599", "band_20_50"])


# --------------------------------------------------------------- FR-1 / FR-2: Purchase friction (keel-cloud 182)

@pytest.mark.parametrize("count, unit, six", [
    (3, "DAYS", ["Under 1 day", "1 to under 3 days", "3 days to 1 week", "1 to 2 weeks", "Over 2 weeks"]),
    (2, "WEEKS", ["Under 1 week", "1 to under 2 weeks", "2 weeks to 1 month", "1 to 3 months", "Over 3 months"]),
    (4, "WEEKS", ["Under 2 weeks", "2 to under 4 weeks", "4 weeks to 3 months", "3 to 6 months", "Over 6 months"]),
    (6, "WEEKS", ["Under 2 weeks", "2 to under 6 weeks", "6 weeks to 3 months", "3 to 6 months", "Over 6 months"]),
    (8, "WEEKS", ["Under 1 month", "1 month to under 8 weeks", "8 weeks to 6 months", "6 months to 1 year",
                  "Over 1 year"]),
    (6, "MONTHS", ["Under 3 months", "3 to under 6 months", "6 months to 1 year", "1 to 2 years", "Over 2 years"]),
    (1, "DAYS", ["Under 1 day", "1 to 3 days", "3 days to 1 week", "1 to 2 weeks", "Over 2 weeks"]),
    (24, "MONTHS", ["Under 3 months", "3 to 6 months", "6 months to 1 year", "1 year to under 24 months",
                    "Over 24 months"]),
])
def test_the_duration_ladder_is_182s_table(count, unit, six):
    """keel-cloud 182 T007's table (`PurchaseFrictionLadderTest`), word for word, then *It wouldn't be needed*."""
    labels = list(friction_mod.labels(friction_mod.Duration(count, unit)).values())
    assert labels == six + [friction_mod.NOT_NEEDED_LABEL]


def test_the_timed_entries_rows_are_codes_six_and_the_sides_are_the_founders_time(registry):
    fresco = _backtest("08-fresco", registry)
    founder = fresco.duration()
    assert founder.said() == "2 weeks"
    assert fresco.respondent_questions[PF]["codes"] == friction_mod.codes(founder) == [
        "days_under_7", "days_7_to_14", "days_14_to_30", "days_30_to_90", "days_over_90", "not_needed"]
    assert [c for c in friction_mod.codes(founder) if friction_mod.within(c, founder)] == [
        "days_under_7", "days_7_to_14", "not_needed"]
    assert [c for c in friction_mod.codes(founder) if friction_mod.longer(c, founder)] == [
        "days_14_to_30", "days_30_to_90", "days_over_90"]
    assert fresco.founder_calibration[PF]["belief_sentence"] == friction_mod.belief(
        "contractor operations leads", "A trial on one live job", founder)
    assert vs.founder_duration(fresco) == {"count": 2, "unit": "WEEKS"}
    assert vs.saved_list(fresco, PF)["duration"] == {"count": 2, "unit": "WEEKS"}
    body = next(a.body for a in vs.calibration_answers(fresco, "COMMERCIAL") if a.dimension == PF)
    assert body["list"]["duration"] == {"count": 2, "unit": "WEEKS"}, "sent on the save (SavedList.duration)"
    cost = next(a.body for a in vs.calibration_answers(fresco, "COMMERCIAL") if a.dimension == SACRIFICE)
    assert "rate" not in cost["cost"], "keel-cloud 180 FR-9: hours stay hours, no rate on the wire"
    # spec 119 re-pin (keel-cloud 187 FR-4 (a), revision 22): no back-test list is untimed now -- Transload names 4 weeks;
    # the undated path is the golden seven's (Paidly's Purchase friction names no time)
    transload = _backtest("12-transload", registry)
    assert transload.duration().said() == "4 weeks" and vs.saved_list(transload, PF)["duration"] == {
        "count": 4, "unit": "WEEKS"}
    untimed = _golden("05-paidly", registry)
    assert untimed.duration() is None and "duration" not in vs.saved_list(untimed, PF)


def test_the_follow_up_on_purchase_friction_is_the_locks_rule():
    """keel-cloud 182 FR-5: the rung on a band from the founder's time (or, with no time, *a long time*); nothing of the
    for side; no second stem."""
    timed = fake.Founder(importance_item="own", price_low=30.0, buyer_supports=(fake.BUYER_ALONE,), friction_days=14)
    pick = lambda c: {"dimension": PF, "codes": [c], "chip": None}  # noqa: E731
    assert fake.first_rung([pick("days_14_to_30")], timed, "COMMERCIAL_B2B", b2b=True) == PF
    assert fake.first_rung([pick("days_7_to_14")], timed, "COMMERCIAL_B2B", b2b=True) is None
    assert fake.first_rung([pick("not_needed")], timed, "COMMERCIAL_B2B", b2b=True) is None
    undated = fake.Founder(importance_item="own", price_low=30.0, buyer_supports=(fake.BUYER_ALONE,))
    assert fake.first_rung([pick("yes_long")], undated, "COMMERCIAL_B2B", b2b=True) == PF
    assert fake.first_rung([pick("yes_quick")], undated, "COMMERCIAL_B2B", b2b=True) is None
    assert PF not in fake.ALSO and fake.ALSO[CO][0] == ("yes_with_steps",)


def test_the_brief_card_counts_those_who_expect_longer(registry):
    fresco = _backtest("08-fresco", registry)
    standing = {"status": "PEOPLE_DISAGREE", "n": 8,
                "optionCounts": "days_under_7=1, days_7_to_14=3, days_14_to_30=3, days_30_to_90=0, days_over_90=0, "
                                "not_needed=1"}
    card = bf.card(fresco, registry.by_key(PF), standing)
    assert (card["number"], card["line"], card["keelBar"], card["statusWords"]) == (
        "3 of 8", "expect a trial on one live job to take longer than 2 weeks",
        "holds if no more than 1 in 3 say it would take longer than you expect", "Did not hold")


# ----------------------------------------------------- FR-2: Ability to pay asked of those at the price (181)

def _ability_item(token="tok"):
    price_id = vs.item_id(token, PRICE)
    return {"itemId": vs.item_id(token, AB), "dimension": AB, "askedAfter": {"itemId": price_id, "answers": [
        {"optionIds": [vs.option_id(token, PRICE, "band_800_2500")],
         "question": "You said about $800 to $2,500 a month. If you went ahead at that, where would the money come from?"},
        {"optionIds": [vs.option_id(token, PRICE, "band_2500_5000")], "question": "You said about $2,500 to $5,000 ..."}]}}


def test_ability_to_pay_is_asked_after_a_price_at_the_founders_and_skipped_after_any_other():
    """keel-cloud 181 T003 / keel-web 155 T020: the item is drawn only after a Price answer listed in `askedAfter`
    (the picks in order equal an entry's `optionIds`), with that entry's question; any other answer skips it."""
    item = _ability_item()
    at = {item["askedAfter"]["itemId"]: {"optionIds": [vs.option_id("tok", PRICE, "band_800_2500")]}}
    below = {item["askedAfter"]["itemId"]: {"optionIds": [vs.option_id("tok", PRICE, "band_500_800")]}}
    refused = {item["askedAfter"]["itemId"]: {"optionIds": [vs.option_id("tok", PRICE, "would_not_pay")]}}
    escaped = {item["askedAfter"]["itemId"]: {"chip": "CANT_SAY"}}
    assert vs.asked_after(item, at) == (True, item["askedAfter"]["answers"][0]["question"])
    for answers in (below, refused, escaped, {}):
        assert vs.asked_after(item, answers) == (False, None)
    plain = {"itemId": "x", "dimension": "commercial.commitment"}
    assert vs.asked_after(plain, {}) == (True, None)
    assert vs.asked_items([plain, item], below) == [plain]
    source = inspect.getsource(vs_screens.Interview._items)
    assert "_asked_items(part.get(\"items\") or [], wire_answers)" in source and "pointed" in source


def test_the_people_not_reached_send_no_ability_answer(registry):
    """Revision 20 deleted the pick of everyone the interview never asks, so the scripted response sends none."""
    fresco = _backtest("08-fresco", registry)
    people = vs.person_inputs(fresco)
    sent = {p.person: [pk.dimension for pk in p.picks] for p in people if p.link == "COMMERCIAL_B2B"}
    assert [who for who, dims in sent.items() if AB in dims] == ["Gordon Achebe"]


def test_the_ai_walk_knows_the_pointed_back_question():
    source = inspect.getsource(il._Walk.__init__)
    assert '(item.get("askedAfter") or {}).get("answers")' in source and "self.items.setdefault" in source


# ----------------------------------------------------- FR-3 / FR-4c(b): Price in two steps (185), the guard

def _price_item():
    labels = ["Under $500", "$500 to under $800", "$800 to under $2,500", "$2,500 to under $5,000", "$5,000 or more",
              "I wouldn't pay for this"]
    return {"itemId": "p", "dimension": PRICE, "options": [{"optionId": str(i), "label": l} for i, l in enumerate(labels)],
            "spoken": {"stem": "What would Fresco be worth to you a month, per site?", "countLine": "I'll read four options.",
                       "optionsLine": "Under $800; $800 to under $2,500; $2,500 or more; or you wouldn't pay for this.",
                       "escapeLine": "Or say you can't say.", "transform": "two_steps",
                       "under": "Under $500, or $500 to under $800?",
                       "over": "$2,500 to under $5,000, or $5,000 or more?"}}


def test_price_is_answered_in_two_steps_as_the_voice_asks_it():
    """keel-cloud 185 FR-3 / keel-web 156 FR-5: a band on a side is said as step one's phrase, then the band at the
    second step (`ai-sheet[data-ask=under|over]`); the middle band and *I wouldn't pay* at once; a lock before 185 (no
    second-step lines) in one ask."""
    item = _price_item()
    assert vs.step_one(item, "$500 to under $800") == ("Under $800", "under")
    assert vs.step_one(item, "Under $500") == ("Under $800", "under")
    assert vs.step_one(item, "$5,000 or more") == ("$2,500 or more", "over")
    assert vs.step_one(item, "$800 to under $2,500") == ("$800 to under $2,500", None)
    assert vs.step_one(item, "I wouldn't pay for this") == ("I wouldn't pay for this", None)
    before = dict(item, spoken={k: v for k, v in item["spoken"].items() if k not in ("under", "over")})
    assert vs.two_steps_of(before) is None and vs.step_one(before, "Under $500") == ("Under $500", None)
    source = inspect.getsource(il._Walk.ladder)
    assert "p.wait_ask(" in source and '("planUnder", "planOver")' in inspect.getsource(il._Walk.answer)
    assert ivs.Player.wait_ask and "data-ask" in inspect.getsource(ivs.Player.sheet)


def test_the_spoken_guard_reads_both_steps():
    """S8: step one's top *or more*; S11: both second-step lines, the side's two bands said whole on money."""
    composed = cloud_mod.ComposedItem(entry="x", key=PRICE, part=3, question="Q?", options=tuple(
        o["label"] for o in _price_item()["options"]), escape="I can't say", anchor=None,
        stem="What would Fresco be worth to you a month, per site?", count_line="I'll read four options.",
        options_line="Under $800; $800 to under $2,500; $2,500 or more; or you wouldn't pay for this.",
        escape_line="Or say you can't say.", transform="two_steps", under="Under $500, or $500 to under $800?",
        over="$2,500 to under $5,000, or $5,000 or more?")
    assert spoken_mod.second_step_faults(composed) == []
    assert [f[:4] for f in spoken_mod.second_step_faults(
        cloud_mod.ComposedItem(**{**composed.__dict__, "under": None}))] == ["S11:"]
    assert spoken_mod.second_step_faults(cloud_mod.ComposedItem(**{**composed.__dict__, "over": "$2,500 or more?"}))
    assert spoken_mod._first_step(list(composed.options)) == ["Under $800", "$800 to under $2,500", "$2,500 or more",
                                                             "I wouldn't pay for this"]


def test_the_record_of_record_keeps_every_spoken_rule(registry):
    """FR-3: the regenerated `build/spoken-corpus.txt` (keel-cloud-docs f3f0d99e) -- Compatibility's three, Price's two
    steps, *Yes, most of the time* -- with no S1-S11 fault on any item."""
    try:
        corpus = corpus_mod.load(KEEL_CLOUD).bind(registry)
        cloud = cloud_mod.read(KEEL_CLOUD, corpus=corpus, registry=registry)
    except Exception as missing:                                        # noqa: BLE001
        pytest.skip(f"no keel-cloud spoken record: {missing}")
    items = [ci for e in corpus.entries for ci in cloud.items_of(e.id)]
    if not any(ci.under for ci in items):
        pytest.skip("the spoken record predates keel-cloud 185 (no second-step lines)")
    faults = [(ci.entry, ci.key, f) for e in corpus.entries for ci in cloud.items_of(e.id)
              for f in spoken_mod.item_faults(ci, registry, e)]
    assert faults == []
    lullaby = {ci.key: ci for ci in cloud.items_of("03-lullaby")}
    assert lullaby[CO].options == tuple(spoken_mod.FACT_ANSWERS.values())
    assert lullaby[CO].count_line == "I'll read three options."
    assert lullaby[PRICE].under and lullaby[PRICE].over


def test_the_reader_screen_says_what_the_voice_says():
    """FR-4c(a): the reader's `{{screen}}` carries the served spoken form whole -- and Price's two second-step lines."""
    said = readers._spoken(_price_item()["spoken"])
    assert "I'll read four options." in said and "Under $500, or $500 to under $800?" in said
    assert "$2,500 to under $5,000, or $5,000 or more?" in said
    assert readers.GUIDELINE_AMENDMENTS[:2] == ("16", "17")      # spec 119 re-pin: and keel-cloud 187's §18 after them


# --------------------------------------------------------- FR-4c(c)-(f): the question and interviewer screens

def test_compatibility_three_on_a_fact_and_most_of_the_time_on_an_ability():
    assert spoken_mod.FACT_ANSWERS == {"yes_easily": "Yes", "yes_with_steps": "Yes, with some steps", "no": "No"}
    assert spoken_mod.ABILITY_ANSWERS["yes_with_steps"] == "Yes, most of the time"
    assert spoken_mod.condition_kind("was your phone within reach", "Their phone was within reach of the cot") == "FACT"
    assert spoken_mod.condition_kind("could you talk over the noise", "They could talk over the noise on site") == \
        "ABILITY"


def test_the_idea_card_names_the_idea_and_says_what_it_is():
    """keel-cloud 185 FR-2 (`IdeaLines.card(name, whatItIs)`): *Imagine {name}, {what it is}.*; the name once where it
    is the plain words; *Imagine {name}.* with none."""
    assert vs.idea_card("Fresco", "notes written from site videos") == "Imagine Fresco, notes written from site videos."
    assert vs.idea_card("Palus", "A higher-yield treasury account.") == "Imagine Palus, a higher-yield treasury account."
    assert vs.idea_card("job sizes predicted", "job sizes predicted") == "Imagine job sizes predicted."
    assert vs.idea_card("Fresco") == vs.idea_card("Fresco", "  ") == "Imagine Fresco."
    assert "idea-what-it-is" in inspect.getsource(vs_screens.Corridor.idea_check)


def test_the_decision_makers_screener_is_the_writers(registry):
    """keel-cloud 185 FR-4: the part-1 job writes `decider_condition` beside the chip; the link serves it; with none
    written, code asks part 1's shape -- never *you decide for*."""
    fresco = _backtest("08-fresco", registry)
    assert vs.decider_screener(fresco) == {"question": DECIDERS["08-fresco"], "inside": "YES"}
    if vs.chip_of(fresco):
        assert vs.respondent_result(fresco, 1, vs.LINK_PRIMARY)["decider_condition"] == vs.decider_screener(fresco)
    served = vs.decider_condition(fresco)
    assert served is None or served["question"] == DECIDERS["08-fresco"]
    # spec 123 FR-4 re-pin (keel-cloud 193 FR-4a): with none written the decision-maker's link asks none (code's
    # part-1 shape, spec 118's fallback, is gone)
    for entry_id in ("05-paidly", "07-mulchrun"):
        assert vs.decider_condition(_golden(entry_id, registry)) is None, entry_id


def test_the_interviewer_screens_say_156s_words():
    """keel-web 156 FR-1 / FR-2, read against its translate.ts."""
    text = (KEEL_WEB / "src" / "lib" / "translate.ts").read_text(encoding="utf-8")
    for word in (ivs.INTERVIEWER_IS, ivs.BEFORE_SEND_LATER, ivs.READ_AND_TAP_LINE, ivs.FORMAT_STATUS_RECORDING,
                 ivs.FORMAT_STATUS_READY, ivs.SEND_TEXT_ONLY_LINKS, iv.READ_AND_TAP):
        assert word in text, word
    assert ivs.send_format_title("construction superintendents") == "How should construction superintendents answer?"
    assert ivs.before_interviewer_title("construction superintendents on commercial jobs") == \
        "Who should ask construction superintendents on commercial jobs your questions?"
    assert ivs.format_status_when_ready("Daphne") == "Ready when Daphne is"
    assert ivs.send_ai_claim("she") == "She catches every spoken answer in a quiet room, and more than 9 in 10 where it " \
                                       "is loud."
    assert iv.FORMAT_NAMES["TEXT"] == "Read and tap" and iv.TEXT_ONLY == "Read and tap"
    from harness import browser as browser_mod                         # noqa: PLC0415
    assert browser_mod.choice_write_label(7) == "Read and tap · about 7 minutes"


# ------------------------------------------- 184 FR-8b (a): Current solution's Answer in keel-web 150's two boxes

def test_current_solutions_answer_is_typed_as_two_boxes(registry):
    """keel-cloud 184 T033: the what box the founder's own words for today's way, the how box its own sentence -- never
    the phrase and the labels joined by *"; "* with no full stop (cycle 4's run-together Answer)."""
    # spec 119 re-pin (keel-cloud 187 FR-4 (b), revision 22): Fresco records what they do today, which is the first box
    # now (`tests/test_cycle_5_to_the_end_119.py`); an entry with no `current_solution.today` keeps 184's phrase -- 22-andy-ai
    entry = _backtest("22-andy-ai", registry)
    text = vs.answer_text(entry, "problem.current_solution_satisfaction")
    what, how = vs_screens.split_answer(text)
    assert entry.today() is None
    assert what == "Getting that visit charted." and how.endswith(".") and how
    assert vs_screens.join_answer(what, how) == text
    assert ";" not in what, "the phrase is a sentence of its own"
    assert vs.founder_rungs(entry) == 2


# --------------------------------------------------------------- FR-4d: one scripted line per follow-up

def test_no_persons_two_follow_ups_receive_the_same_text(registry):
    """keel-cloud 180 not foreseen 3: the AirCaps walk typed the same scripted why into both of a person's two
    follow-ups. The entry carries one why a person; a second follow-up is skipped, never answered with it again --
    on every back-test person who has a line, whatever two rungs they are asked."""
    line = lambda rung, _t="Proof that it pays back.": _t  # noqa: E731
    owed = cs.follow_up_lines_owed([{"dimension": PRICE}, {"dimension": "commercial.buyer_payer_alignment"}], line)
    assert owed == {PRICE: "Proof that it pays back.", "commercial.buyer_payer_alignment": None}
    assert vs_screens.distinct_follow_up("Same.", ["same."]) is None and vs_screens.distinct_follow_up("A.", []) == "A."
    for path in sorted(corpus_mod.backtest_dir(KEEL_CLOUD).glob("*.yaml")):
        entry = corpus_mod.load_file(path, registry=registry, backtest=True)
        for person in vs.person_inputs(entry):
            plan = [{"dimension": r} for r in fake.RUNGS[:2]]
            typed = [t for t in cs.follow_up_lines_owed(plan, lambda rung, _p=person: vs.follow_up_line(
                entry, _p, {"dimension": rung})).values() if t]
            assert len(typed) == len(set(typed)), (entry.id, person.person, typed)


# ---------------------------------------------------------------- 183: the one why goes where it is fewest

def test_the_fewest_failing_line_goes_first():
    owed = [(PRICE, False), ("commercial.buyer_payer_alignment", False), (PF, False), ("commercial.commitment", True)]
    failing = {PRICE, PF, "commercial.commitment"}
    assert [o[0] for o in fake.fewest_first(owed, failing, {PRICE: 3, PF: 1})] == [
        "commercial.commitment", PF, PRICE, "commercial.buyer_payer_alignment"]
    assert fake.fewest_first(owed, set(), {}) == owed, "no failing line keeps the walk whole"
    assert [o[0] for o in fake.fewest_first(owed, {PRICE, PF}, {})] == [PRICE, PF, "commercial.buyer_payer_alignment",
                                                                         "commercial.commitment"], "a tie: registry order"


def test_compatibilitys_second_stem_only_where_the_answer_says_its_steps():
    ability = fake.Founder(importance_item="own", compatibility_steps=False)
    fact = fake.Founder(importance_item="own", compatibility_steps=True)
    pick = {"dimension": CO, "codes": ["yes_with_steps"], "chip": None}
    assert fake.owed([pick], fact) == [(CO, True)] and fake.owed([pick], ability) == []
    assert fake.ALSO[CO][1] == "What steps did it take?"


# ------------------------------------------------- FR-4: the after-answers leg reads keel-web 155's lines

_CARD_155 = """<main><div class="corridor answers" data-testid="stage-page" data-stage="COMMERCIAL">
<p class="answers__headline" data-testid="stage-verdict">Not holding up · Price: 1 of 8 at $800 or more</p>
<p data-testid="stage-tally">2 holding · 1 not holding · 2 did not hold · 1 split</p>
<div class="dimrow" id="commercial.price" data-testid="stage-dimension" data-dim="commercial.price" data-opens="true"
  data-open="true"><button class="dimrow__head" data-testid="stage-dimension-open">open</button>
  <span class="dimrow__name">Price</span><span class="status" data-testid="dimension-verdict">Not holding up
  <span class="sub" data-testid="dimension-count">1 of 8 at $800 or more · bar 6 of 8</span></span>
  <div class="dimrow__body"><p data-testid="dimension-asked">"What would Fresco be worth to you a month, per site?" — if
  it were offered today</p><p data-testid="dimension-rule">Counts for you: $800 or more. Counts against: under $800, or
  would not pay.</p><div class="dimrow__drawing" data-testid="dimension-chart"><ul class="dimbars">
  <li class="dimbar dimbar--against" data-side="AGAINST"><span>$500 to under $800</span><b class="dimbar__side">against</b></li>
  <li class="dimbar dimbar--for" data-side="FOR" data-founder-band><span>$800 to under $2,500</span>
  <b class="dimbar__side">for</b></li></ul><p data-testid="founder-range">your $800 to $1,000 sits here</p>
  %s</div>
  <p data-testid="dimension-count-line">8 answered · 8 counted · 5 under $500 · 2 at $500 to under $800</p>
  <p class="dimrow__so" data-testid="dimension-so">Fewer than 2 in 3 would pay $800.</p>
  <ul class="dimpeople"><li data-testid="dimension-person" data-side="FOR"><span>Gordon Pike</span>
  <span class="dimpeople__read">$800 to under $2,500 · at your price or more</span></li>
  <li data-testid="dimension-person" data-side="NOT_COUNTED"><span>Omar</span><span class="dimpeople__read">gave no
  price<span class="dimpeople__why" data-testid="dimension-person-why"> · gave no price</span></span></li></ul>
  </div></div></div></main>"""
_STRIP = """<div data-testid="bar-strip" data-mode="cells" data-counted="8" data-bar="6">
  <p data-testid="bar-strip-label">your bar · 6 of 8 (at least 2 in 3)</p>
  <i class="barstrip__cell" data-side="FOR" data-kind="for"></i><i class="barstrip__cell" data-side="AGAINST"
  data-kind="against"></i><i class="barstrip__cell" data-side="AGAINST" data-kind="refusal"></i>
  <span data-testid="bar-strip-marker">bar</span></div>"""
_INSIGHTS_155 = """<div data-testid="report-insights"><section class="rp-ibox" data-dim="commercial.price"
  data-status="NOT_HOLDING_UP" data-state="GROUPED"><h3 class="rp-ihead">Price · Not holding up</h3>
  <p class="rp-istatus" data-testid="insights-status-line">1 of 8 at $800 or more · bar 6 of 8</p>
  <p data-testid="insights-belief">Contractor operations leads would think Fresco worth $800 to $1,000.</p>
  <p class="rp-concern">What would make it worth more?</p>
  <p data-testid="insights-count-line">7 against · 3 asked their why here · 4 asked on Buyer and payer</p>
  <div data-testid="insights-also">What would make it clearly worth it?</div></section></div>"""


@pytest.fixture(scope="module")
def browser():
    with sync_playwright() as p:
        b = p.chromium.launch()
        yield b
        b.close()


def test_the_leg_reads_the_strip_and_the_served_lines_and_a_card_with_none(browser):
    page = browser.new_page()
    try:
        page.set_content(_CARD_155 % _STRIP)
        stage = page.evaluate(bt.STAGE_JS)["page"]
        card = page.evaluate(bt.CARD_JS, PRICE)
        page.set_content(_CARD_155 % "")
        bare = page.evaluate(bt.CARD_JS, PRICE)
        page.set_content(_INSIGHTS_155)
        insights = page.evaluate(bt.INSIGHTS_JS)["insights"]
    finally:
        page.close()
    assert stage["tally"] == "2 holding · 1 not holding · 2 did not hold · 1 split"
    chart = card["chart"]
    assert card["strip_drawn"] is True and bare["strip_drawn"] is False and bare["chart"]["strips"] == []
    strip = chart["strips"][0]
    assert (strip["mode"], strip["counted"], strip["bar"]) == ("cells", "8", "6")
    assert strip["label"] == "your bar · 6 of 8 (at least 2 in 3)" and strip["marker"] == "bar"
    assert strip["sides"] == {"FOR": 1, "AGAINST": 2} and strip["kinds"] == {"for": 1, "against": 1, "refusal": 1}
    assert chart["rule"].startswith("Counts for you: $800 or more.")
    assert chart["count_line"].startswith("8 answered · 8 counted") and chart["so"].startswith("Fewer than 2 in 3")
    assert chart["asked_line"].endswith("if it were offered today")
    assert [b["side"] for b in chart["bars"]] == ["AGAINST", "FOR"] and chart["bars"][1]["founder_band"] is True
    assert chart["marks"]["founder-range"] == "your $800 to $1,000 sits here"
    assert [(p["name"], p["side"]) for p in chart["people"]] == [("Gordon Pike", "FOR"), ("Omar", "NOT_COUNTED")]
    assert chart["people"][1]["why"] == "· gave no price"
    box = insights["boxes"][0]
    assert box["status_line"] == "1 of 8 at $800 or more · bar 6 of 8"
    assert box["belief"].startswith("Contractor operations leads") and box["count_line"].startswith("7 against")
    assert box["also"] == "What would make it clearly worth it?"
    body, _ = readers._after_body({"kind": "dimension", "n": 2, "stage": "COMMERCIAL", "dimension": PRICE,
                                   "chart": chart}, 3)
    said = "\n".join(body)
    assert "The strip under the chart" in said and "The count line" in said and "The So line" in said
    assert "counts for you" in said and "not counted" in said


# ------------------------------------------------------------- the leg's founder steps (155: time, loss line)

def test_choose_types_the_founders_time_and_the_cost_step_the_loss_line():
    choose = inspect.getsource(vs_screens.Corridor.list_choose)
    assert "DURATION_COUNT_TESTID" in choose and "select_option(value=str(duration[\"unit\"]))" in choose
    assert "duration=duration" in inspect.getsource(cs.leg_calibrate)
    cost = inspect.getsource(vs_screens.Corridor._chain_cost)
    assert 'get_by_test_id("chain-loss")' in cost and "lossPhrase" in cost
    assert vs_screens.sent_duration([{"status": 200, "body": {"answers": [
        {"dimension": PF, "list": {"duration": {"count": 2, "unit": "WEEKS"}}}]}}], PF) == {"count": 2, "unit": "WEEKS"}


def test_the_brief_mirrors_are_180s_and_182s(registry):
    """FR-1: every golden card agrees with keel-cloud's build of record (`build/brief-facts/` at f3f0d99e) -- pinned
    here on the moved lines: every yes the number, the conditional ones *of them* beside it; the friction card's line
    and bar; *Not reached* in the words."""
    lullaby = _golden("03-lullaby", registry)
    cards = {c["key"]: c for c in bf.cards_for(lullaby, registry)}
    assert cards["solution.adoption_friction"]["line"].endswith("· 2 of them if it was clearly worth it")
    assert cards["commercial.commitment"]["line"].endswith("· 4 of them after a look at how it listens first")
    assert bf.VERDICT_WORDS["NOT_REACHED"] == "Not reached"
    assert not hasattr(bf, "retense_179")
