"""Spec 119 -- the harness walks cycle 5's studies to the end, and the reader hears what the voice says.

Against keel-cloud-docs `bc172359` (keel-cloud 187 + 188: contract 56, corpus revision 22; its build records of record)
and keel-web `f02595c` (158 + 159). Cycle 5 (`quality/cycles/20261101-e65afec.md`) stopped nine of fifteen walks; the
stops that were the harness's are replayed here on fixtures cut from the recorded bundles (`tests/fixtures/cycle5/`):
the idea line (10-palus and 13-aircaps COMMERCIAL), Ability to pay's written question (17-expanse COMMERCIAL), the
Choose time (21-codyco COMMERCIAL, corpus revision 22) and the waiting state scored as a screen (10-palus SOLUTION);
the reader's spoken form on the text link and the spoken guard's escape, percent step and duration bands on the Palus
items as served. Where keel-cloud's checkout lacks a record the test skips by name.
"""

from __future__ import annotations

import inspect
import json
from contextlib import contextmanager
from pathlib import Path
from types import SimpleNamespace

import pytest
import yaml
from playwright.sync_api import sync_playwright

from evals import backtest as bt
from evals import corpus_scenario as cs
from evals import scope_journey as sj
from harness import vectors_screens as vs_screens
from harness import vectors_script as vs
from instructions import cloud_corpus as cloud_mod
from instructions import corpus as corpus_mod
from instructions import friction as friction_mod
from instructions import spoken as spoken_mod
from quality import readers
from stack.config import load_config

KEEL_CLOUD = Path(load_config(validate=False).keel_cloud)
MIRROR = KEEL_CLOUD / "src" / "test" / "resources" / "keel"
FIXTURES = Path(__file__).parent / "fixtures" / "cycle5"
AB, PF, PRICE = "commercial.ability_to_pay", "commercial.purchase_friction", "commercial.price"
CS_KEY = "problem.current_solution_satisfaction"
_ABSENT = object()


def _fixture(name: str) -> dict:
    return json.loads((FIXTURES / name).read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def registry():
    try:
        return cloud_mod.registry_of_record(KEEL_CLOUD)
    except Exception as missing:                                        # noqa: BLE001
        pytest.skip(f"no keel-cloud registry of record: {missing}")


def _backtest(entry_id: str, registry=None):
    path = corpus_mod.backtest_dir(KEEL_CLOUD) / f"{entry_id}.yaml"
    if not path.is_file():
        pytest.skip(f"no back-test entry {entry_id} at {path.parent}")
    return corpus_mod.load_file(path, registry=registry, backtest=True)


class _Held:
    def __init__(self):
        self.recorded = []

    def record_assert(self, want, got):
        self.recorded.append((want, got))

    def record_wire(self, want, got):
        self.recorded.append((want, got))


class _Recorder:
    """A recorder whose steps hold nothing but the record: an assertion inside raises as the journey's would."""

    def __init__(self):
        self.steps = []

    @contextmanager
    def step(self, name, party=None, kind=None):
        held = _Held()
        self.steps.append((name, held))
        yield held


def _journey(**fields):
    return SimpleNamespace(recorder=_Recorder(), strict=False, findings=[], changed={}, **fields)


# ----------------------------------------------------------------------------------------- FR-1 the idea's line

def test_palus_commercial_holds_the_served_line_it_stopped_on():
    """10-palus COMMERCIAL stopped on Sofia Marchetti: the check composed *Imagine Palus.* (money alone never read the
    plain words) beside the served *Imagine Palus, a managed reserve portfolio.*. Now the served line is the card: it
    names the idea, and the drawn card opens with it."""
    fx = _fixture("10-palus-commercial.json")
    read = fx["founder_idea_read"]
    j = _journey(idea_name=read["shortName"], idea_what_it_is=read["whatItIs"], idea_line=read["line"])
    walked = {"screens": fx["drawn"]}
    cs._hold_the_idea_name(j, SimpleNamespace(person=fx["person"]), fx["interview"], walked)     # no raise
    assert fx["interview"]["idea"]["what"] == read["line"] == "Imagine Palus, a managed reserve portfolio."
    # the composed card without the plain words (cycle 5's want) is never the want again
    assert vs.idea_card("Palus") == "Imagine Palus." != read["line"]


def test_aircaps_commercial_reveal_opens_with_the_served_line():
    """13-aircaps COMMERCIAL stopped on Harriet Coleman's reveal (money alone on the person's own link)."""
    fx = _fixture("13-aircaps-commercial.json")
    read = fx["founder_idea_read"]
    j = _journey(idea_name="AirCaps", idea_what_it_is=read["whatItIs"], idea_line=read["line"])
    interview = {"reveal": fx["served_reveal"], "idea": fx["served_idea"], "parts": []}
    cs._hold_the_idea_name(j, SimpleNamespace(person=fx["person"]), interview, {"screens": fx["drawn"]})
    assert fx["drawn"] and fx["drawn"][0]["card"].startswith("Imagine AirCaps, live captions inside the lens.")


def test_the_idea_line_faults_name_what_is_wrong():
    """`idea_line_faults`: a served line that does not name the idea, a line other than the founder's read, a card that
    does not open with the line, and the Relative advantage card -- each a fault; keel-cloud 188's empty plain words
    (*Imagine Fresco.*) hold."""
    served = [("idea", {"what": "Imagine Palus, a treasury account."})]
    card = {"screen": "idea", "card": "Imagine Palus, a treasury account.\n\nYou link ..."}
    assert cs.idea_line_faults("Palus", served, [card], want="Imagine Palus, a treasury account.") == []
    assert cs.idea_line_faults("Palus", served, [card]) == []                 # no read of the founder's line: names it
    assert cs.idea_line_faults("Fresco", [("idea", {"what": "Imagine Fresco."})],
                               [{"screen": "idea", "card": "Imagine Fresco.\n\nDuring the site walk ..."}],
                               want="Imagine Fresco.") == []
    wrong = cs.idea_line_faults("Palus", [("idea", {"what": "Imagine a treasury account."})], [])
    assert wrong and "names the idea" in json.dumps(wrong)
    other = cs.idea_line_faults("Palus", [("idea", {"what": "Imagine Palus."})], [],
                                want="Imagine Palus, a treasury account.")
    assert other and other[0]["want"] == "Imagine Palus, a treasury account."
    drawn = cs.idea_line_faults("Palus", served, [{"screen": "idea", "card": "Imagine Palus.\n\nYou link ..."}])
    assert drawn and drawn[0]["screen"] == "idea"
    ra = cs.idea_line_faults("Palus", served, [{"screen": "item", "dimension": cs.RA_KEY,
                                                "idea_card": "Imagine Palus."}])
    assert ra and ra[0]["screen"] == "item"


def test_money_alone_and_s2_keep_the_founders_line():
    """Both founder idea steps keep `IdeaView.line` and `whatItIs` for the strangers' check (money alone did not)."""
    assert 'j.idea_line = idea.get("line") or None' in inspect.getsource(sj.leg_idea_card)
    assert 'j.idea_what_it_is = idea.get("whatItIs")' in inspect.getsource(sj.leg_idea_card)
    assert 'j.idea_line = idea.get("line") or None' in inspect.getsource(cs)
    assert "idea_line_faults(name, served" in inspect.getsource(cs._hold_the_idea_name)


# -------------------------------------------------------------------------- FR-2 Ability to pay's written question

def test_expanse_ability_to_pay_holds_the_written_question_drawn():
    """17-expanse COMMERCIAL stopped on Gregory Lindqvist: the drawn *You said about $10,000 to $25,000 a month. ...* was
    held to the item's `question`, the one spoken sentence (*Think of the price you just gave. ...*). The page draws the
    written one for the person's Price answer -- the walk's `pointed_back`, or the `askedAfter` entry of the sent answer."""
    fx = _fixture("17-expanse-commercial.json")
    drawn = next(d for d in fx["drawn"] if d["dimension"] == AB)
    recorded = fx["failed_step"]["response"][0]
    assert recorded["screen"]["question"] != recorded["wire"]["question"], "cycle 5's stop, as recorded"
    item = {"itemId": "ab", "dimension": AB, "question": recorded["wire"]["question"],
            "askedAfter": {"itemId": "price", "answers": [
                {"optionIds": ["p2"], "question": drawn["question"]},
                {"optionIds": ["p3"], "question": "You said about $25,000 to $50,000 a month. If you went ahead at that, "
                                                  "where would the money come from?"}]}}
    met = {"pointed_back": [{"dimension": AB, "question": drawn["question"], "drawn": drawn["question"]}]}
    assert cs.pointed_back_question(item, met) == drawn["question"]
    sent = {"body": {"answers": [{"itemId": "price", "optionIds": ["p2"]}]}}
    assert cs.pointed_back_question(item, sent) == drawn["question"]
    assert cs.pointed_back_question({"dimension": PRICE, "question": "What ...?"}, met) is None
    held = inspect.getsource(cs._hold_the_screens)
    assert "written = pointed_back_question(item, walked)" in held and 'want["question"] = written' in held
    assert '"pointed_back": list(self.pointed_back)' in inspect.getsource(vs_screens.Interview.walk)


# ------------------------------------------------------------------------------- FR-3 / FR-6 the Choose time, r22

def test_every_b2b_back_test_entry_names_the_founders_time(registry):
    """keel-cloud 187 FR-4 (a): all 16 B2B entries name a time, and the walk types it on Choose and sends it on the save
    -- Codyco's 4 weeks among them (cycle 5 stuck on its Choose, Continue waiting for a time the entry did not name)."""
    entries = [e for e in corpus_mod.load(KEEL_CLOUD, registry=registry, backtest=True).entries if e.b2b()]
    assert len(entries) == 16
    for entry in entries:
        duration = vs.founder_duration(entry)
        assert duration and entry.duration().valid(), entry.id
        assert vs.saved_list(entry, PF)["duration"] == duration, entry.id
        assert entry.respondent_questions[PF]["codes"] == friction_mod.codes(entry.duration()), entry.id
        assert entry.respondent_questions[PF]["escape"] == "cant_tell", entry.id
    codyco = next(e for e in entries if e.id == "21-codyco")
    assert vs.founder_duration(codyco) == {"count": 4, "unit": "WEEKS"}


def test_choose_stops_by_name_where_the_box_asks_a_time_the_entry_lacks():
    choose = inspect.getsource(vs_screens.Corridor.list_choose)
    assert "if drawn_duration.count() and not duration:" in choose and "names no time" in choose


_CHOOSE = """<main><p class="corridor__kicker">Step 4 of 5 · Will they pay · What do you believe is true?</p>
<p class="corridor__intro">The person who decides gets one question for this: if they bought it, how long would this
step take before it went through. Pick the one step.</p>
<div class="listcheck"><h2 class="listcheck__title">Which one do you want to test?</h2><div role="radiogroup">
<div role="radio" aria-checked="false">A data protection review of guest calls</div>
<div role="radio" aria-checked="false">A trial at one hotel first</div></div></div>
<div class="calib__duration" data-testid="duration-input"><p class="calib__durationq">How long do you expect this step
to take?</p><div class="calib__nums"><input data-testid="duration-count" value=""><select data-testid="duration-unit">
<option value="DAYS">days</option><option value="WEEKS" selected>weeks</option><option value="MONTHS">months</option>
</select></div><p class="calib__hint">Your own estimate, as a whole number. Strangers are asked how long it would take
them.</p></div>
<div class="keeltest"><p class="keeltest__t">Pick one and the test appears here.</p><p class="keeltest__b">Holds if no
more than 1 in 3 say it would take longer than you expect.</p></div></main>"""


@pytest.fixture(scope="module")
def browser():
    with sync_playwright() as p:
        b = p.chromium.launch()
        yield b
        b.close()


def test_the_reader_is_handed_the_choose_time_box_and_the_bar(browser):
    """21-codyco's founder-reader scored *no number box* (R2 = 0) on a Choose that drew one: the shot now carries the
    title, the intro, the time box (its question, the box and unit menu, its hint) and the *Keel will test* box."""
    page = browser.new_page()
    try:
        page.set_content(_CHOOSE)
        shot = page.evaluate(bt.READ_JS)
    finally:
        page.close()
    assert shot["title"] == "Which one do you want to test?"
    assert shot["time_box"]["question"].startswith("How long do you expect this step")
    assert shot["time_box"]["unit"] == "weeks" and shot["time_box"]["units"] == ["days", "weeks", "months"]
    assert shot["time_box"]["hint"].startswith("Your own estimate")
    assert shot["keel_test"]["bar"].startswith("Holds if no more than 1 in 3")
    record = {"n": 19, "screen": "choose-commercial.purchase_friction", "kicker": shot["kicker"], "question": "",
              "hint": shot["hint"], "options": shot["options"],
              **{k: shot[k] for k in ("title", "intro", "time_box", "keel_test") if shot.get(k)},
              "answer": {"pickedIndex": 0, "the founder's time (typed in the box)": {"count": "4", "unit": "WEEKS"}}}
    screen = readers.founder_screens({"founder_screens": [record]})[0]
    assert "Title over the list: Which one do you want to test?" in screen.full
    assert "a time box: How long do you expect this step to take? -- a number box and a unit menu" in screen.full
    assert "Its hint: Your own estimate" in screen.full
    assert "the *Keel will test* box: Pick one and the test appears here. (the bar: Holds if no more than 1 in 3" \
        in screen.full


# ------------------------------------------------------------------------------ FR-6 corpus revision 22, read

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


def _one_rule(code, founder):
    """182 T020's one rule: `yes_quick` -> the band just under the founder's time, `yes_long` -> the band from it."""
    days = friction_mod.Duration.of(founder).days()
    bands = friction_mod.bands(friction_mod.Duration.of(founder))
    under = next(c for c, lo, hi, _ in bands if hi == days)
    from_ = next(c for c, lo, hi, _ in bands if lo == days)
    return {"yes_quick": under, "yes_long": from_}.get(code, code)


#: keel-cloud 187 FR-4 (a): the 13 entries revision 22 times, and the time.
TIMED_22 = {"12-transload": (4, "WEEKS"), "14-code-four": (8, "WEEKS"), "15-voltair": (3, "MONTHS"),
            "16-pairio": (6, "WEEKS"), "18-careforce": (6, "WEEKS"), "19-veles": (2, "WEEKS"), "20-lemma": (3, "WEEKS"),
            "21-codyco": (4, "WEEKS"), "22-andy-ai": (2, "WEEKS"), "25-bidflow": (1, "WEEKS"),
            "26-cubic": (4, "WEEKS"), "27-blacksmith": (3, "WEEKS"), "28-relvy-ai": (4, "WEEKS")}
#: keel-cloud 187 FR-4 (b): the 14 entries that record what they do today.
TODAY = {f"{n:02d}-" for n in range(8, 22)}


#: Spec 123 FR-1: the head of every back-test entry keel-cloud 193 amended in place (revision 22 kept).
AMENDED_193 = "# AMENDED IN PLACE (keel-cloud spec 193 FR-1"
#: Spec 130: keel-cloud 199 FR-10's note, at the head of the three it amended in place again (above 193's).
AMENDED_199 = "# AMENDED IN PLACE (keel-cloud spec 199 FR-10"
ES = "commercial.existing_sacrifice"


def test_revision_22_moves_exactly_187s_edits():
    """D22, the revision-21 record beside canon: the revision line (21 -> 22); on 13 B2B back-test entries the founder's
    time beside Purchase friction, its belief in the dated form, the row (control, codes, escape) code's six and every
    pick moved by 182's one rule (Transload's chip read `cant_tell`); `current_solution.today` on the 14 entries 08-21;
    the golden seven their revision line alone; nothing else, no `expected` anywhere."""
    # spec 132 FR-11 re-pin (keel-cloud 207, corpus revision 23): canon has moved on to 23, so the revision-22 records
    # (`corpus-r22/`, `backtest-r22/`, kept by 207) stand for revision 22 here; 22 -> 23 is
    # `test_cloud_205_208_mirror_132.py`'s
    for rev in ("corpus-r21", "backtest-r21", "corpus-r22", "backtest-r22"):
        if not (MIRROR / rev).is_dir():
            pytest.skip(f"keel-cloud at {KEEL_CLOUD} carries no {rev} record")
    moved, today, strays, amended, amended_199 = 0, set(), [], set(), set()
    for kind, canon in (("corpus", MIRROR / "corpus-r22"), ("backtest", MIRROR / "backtest-r22")):
        for path in sorted(canon.glob("*.yaml")):
            before, after = _load(MIRROR / f"{kind}-r21" / path.name), _load(path)
            entry = after["id"]
            out: list = []
            _walk(before, after, (), out)
            for p, old, new in out:
                if p == ("revision",):
                    assert (old, new) == (21, 22), entry
                elif p == ("current_solution",):
                    assert old is _ABSENT and set(new) == {"today"} and entry[:3] in TODAY, entry
                    assert len(new["today"].split()) <= corpus_mod.TODAY_MAX_WORDS, entry
                    today.add(entry)
                elif kind == "backtest" and entry in TIMED_22 and p == ("founder_calibration", PF, "answer", "duration"):
                    assert old is _ABSENT and (new["count"], new["unit"]) == TIMED_22[entry], (entry, new)
                elif kind == "backtest" and p == ("founder_calibration", ES, "belief_phrase") \
                        and path.read_text(encoding="utf-8").startswith(AMENDED_199):
                    # spec 130 (keel-cloud 199 FR-10): amended in place again -- the base said once, *per {unit}* dropped
                    # where the base names the unit (17-expanse, 20-lemma, 23-taiga)
                    unit = (after["founder_calibration"][ES]["answer"] or {}).get("unit")
                    assert old.replace(f" per {unit}", "") == new, (entry, old, new)
                    amended_199.add(entry)
                elif kind == "backtest" and p == ("founder_calibration", ES, "belief_sentence") \
                        and AMENDED_193 in path.read_text(encoding="utf-8"):
                    # spec 123 FR-1 (keel-cloud 193 FR-1): revision 22 amended in place -- the Existing sacrifice
                    # sentence names who really spends; the load holds it to the engine's (`chain.cost_belief`)
                    assert old != new and ("already" in new or new.startswith("About ")), (entry, new)
                    amended.add(entry)
                elif kind == "backtest" and entry in TIMED_22 and p == ("founder_calibration", PF, "belief_sentence"):
                    assert "within about" in new, (entry, new)
                elif kind == "backtest" and entry in TIMED_22 and p[:2] == ("respondent_questions", PF):
                    assert p[2] in ("control", "escape", "codes"), (entry, p)
                elif kind == "backtest" and entry in TIMED_22 and len(p) >= 4 and p[0] == "answers" \
                        and p[2:4] == ("picks", PF):
                    founder = {"count": TIMED_22[entry][0], "unit": TIMED_22[entry][1]}
                    if p[4:] == ("chip",):
                        assert (entry, old, new) == ("12-transload", "cant_recall", "cant_tell"), (entry, p)
                    else:
                        assert new == _one_rule(old, founder), (entry, p, old, new)
                        moved += 1
                else:
                    strays.append((entry, p, old, new))
            assert before.get("expected") == after.get("expected"), entry
    assert not strays, strays[:20]
    assert len(today) == 14 and moved == 80, (sorted(today), moved)
    # keel-cloud 193's 17 entries (08-14, 16-23, 26, 28), each with its AMENDED IN PLACE note
    assert len(amended) == 17, sorted(amended)
    # spec 130: keel-cloud 199 FR-10's three, the belief phrase amended in place beside 193's sentence
    assert sorted(amended_199) == ["17-expanse", "20-lemma", "23-taiga"], sorted(amended_199)


def test_every_entry_loads_at_22_and_21_is_refused_by_name(tmp_path, registry):
    record = MIRROR / "backtest-r21" / "21-codyco.yaml"
    if not record.is_file():
        pytest.skip("no r21 record")
    (tmp_path / "21-codyco.yaml").write_text(record.read_text(encoding="utf-8"), encoding="utf-8")
    # spec 135 (keel-cloud 215): 21-codyco is a gallery entry, read at revision 24
    with pytest.raises(corpus_mod.CorpusError, match="revision is 21; this eval reads revision 24 for a gallery entry "
                                                     "only -- revision 21 is MARKS_VERSION 24's corpus before keel-cloud "
                                                     "187"):
        corpus_mod.load_file(tmp_path / "21-codyco.yaml", registry=registry, backtest=True)


def test_current_solution_today_is_read_and_held(tmp_path, registry):
    codyco = _backtest("21-codyco", registry)
    assert codyco.today() == ("A central reservations office or a call center answers what it can; calls after hours, "
                              "at peak and on holidays ring out.")
    assert _backtest("22-andy-ai", registry).today() is None
    raw = _load(corpus_mod.backtest_dir(KEEL_CLOUD) / "21-codyco.yaml")
    raw["current_solution"] = {"today": " ".join(["word"] * 26)}
    (tmp_path / "21-codyco.yaml").write_text(yaml.safe_dump(raw, sort_keys=False), encoding="utf-8")
    with pytest.raises(corpus_mod.CorpusError, match="current_solution.today is 26 words; at most 25"):
        corpus_mod.load_file(tmp_path / "21-codyco.yaml", registry=registry, backtest=True)
    raw["current_solution"] = {"today": "x", "how": "y"}
    (tmp_path / "21-codyco.yaml").write_text(yaml.safe_dump(raw, sort_keys=False), encoding="utf-8")
    with pytest.raises(corpus_mod.CorpusError, match="revision 22 records `{today: <one sentence>}`"):
        corpus_mod.load_file(tmp_path / "21-codyco.yaml", registry=registry, backtest=True)


def test_the_answer_types_today_in_the_first_box_within_the_answers_25_words(registry):
    """keel-cloud 184 FR-8b (a) with 187 FR-4 (b): the first box is the entry's own sentence for today's way, the rungs
    the second within what is left of the Answer's 25 words (keel-cloud's `ANSWER_MAX_WORDS` holds the two joined) --
    on the 14 entries no rung fits beside today's sentence, so the Check screen types them back (spec 067 FR-2)."""
    for entry in corpus_mod.load(KEEL_CLOUD, registry=registry, backtest=True).entries:
        what, how = vs.current_solution_boxes(entry)
        text = vs.answer_text(entry, CS_KEY)
        assert len(text.split()) <= vs.ANSWER_MAX_WORDS, (entry.id, text)
        assert vs_screens.split_answer(text) == (what, how), entry.id
        if entry.today():
            assert what == entry.today() if entry.today().endswith(".") else what == entry.today() + ".", entry.id
    fresco = _backtest("08-fresco", registry)
    assert vs.current_solution_boxes(fresco)[0] == ("They take photos on their site walks, then upload them and type "
                                                    "the daily log in the trailer at the end of the day.")


# ------------------------------------------------------------------------- FR-4 the reader hears the voice

def test_the_bundle_records_the_served_spoken_form_and_the_reader_says_it():
    """10-palus COMMERCIAL's Price on the text link: the reader composed §3's template from the written list (*the bundle
    records no spoken form for it*) because `served_items` dropped the item's `spoken`. Recorded now on every item, the
    plan's too, beside `askedAfter`'s written questions; the reader's `{{screen}}` says the served lines, Price's second
    step and the duration bands' with it."""
    fx = _fixture("10-palus-commercial.json")
    served = bt.served_items(fx["interview"])
    items = {i["dimension"]: i for p in served["parts"] for i in p["items"]}
    assert items[PRICE]["spoken"]["optionsLine"].startswith("Under a quarter of a percent")
    assert items[PF]["spoken"]["under"] == "Under 2 weeks, or 2 to under 4 weeks?"
    assert items[AB]["spoken"]["anchor"] == "Think of the price you just gave."
    assert [a["question"] for a in items[AB]["askedAfter"]["answers"]][0].startswith("You said about")
    screens = readers.respondent_screens({"respondents": {"COMMERCIAL_B2B": {"served": served, "drawn": fx["drawn"]}}})
    said = {s.screen: s for s in screens["COMMERCIAL_B2B"]}
    for name in ("item-commercial.price", "item-commercial.purchase_friction"):
        assert "records no spoken form" not in said[name].full, name
        assert "(the served spoken form)" in said[name].full, name
    assert "half a percent or more; or you wouldn't pay for this." in said["item-commercial.price"].said
    assert "On the upper side: Half to under one percent, or one percent or more?" in said["item-commercial.price"].said
    assert "on the lower side: Under 2 weeks, or 2 to under 4 weeks?" in said["item-commercial.purchase_friction"].said


def test_a_served_item_with_no_spoken_block_records_none():
    row = bt.served_items({"parts": [{"part": 3, "items": [{"dimension": PRICE, "question": "Q?", "options": []}]}]})
    assert "spoken" not in row["parts"][0]["items"][0]


# ------------------------------------------------------------------------------------------ FR-5 the guard

def test_the_guard_reads_palus_three_items_clean(registry):
    """Cycle 5's three red rows on Palus (the recorded faults, kept in the fixture): S8 on the percent ladder's first
    step, S6 on Ability to pay's *I can't say*, S3 / S7 / S8 / S9 on the duration bands. Each is the record as keel-cloud
    serves it -- read through the registry of record (the export's), no pinned label -- so each is clean now."""
    fx = _fixture("10-palus-commercial.json")
    recorded = {r["dimension"]: r["faults"] for r in fx["recorded_guard_red"]}
    assert set(recorded) == {PRICE, AB, PF}
    assert any(f.startswith("S6") for f in recorded[AB]) and any(f.startswith("S9") for f in recorded[PF])
    palus = _backtest("10-palus", registry)
    j = SimpleNamespace(entry=palus, registry=registry, interviews={fx["person"]: fx["interview"]})
    guard = bt.spoken_guard(j)
    rows = {r["dimension"]: r for r in guard["rows"]}
    assert rows[PRICE]["faults"] == [] and rows[AB]["faults"] == [] and rows[PF]["faults"] == [], rows
    assert guard["red"] == []


def test_the_pointed_back_escape_is_prices_row_in_the_export(registry):
    """keel-cloud 181 (`CommercialChain.side`): where Ability to pay points back, its escape is Price's own -- read off
    the registry the item was served from; the registry's own row still names *I can't recall one*."""
    palus = _backtest("10-palus", registry)
    assert registry.by_key(AB).escape["label"] == "I can't recall one"
    assert spoken_mod.points_back(palus, AB)
    assert spoken_mod.item_escape(registry, AB, palus) == spoken_mod.served_escape(registry, AB, palus) == \
        registry.by_key(PRICE).escape["label"] == "I can't say"
    golden = corpus_mod.load_file(corpus_mod.corpus_dir(KEEL_CLOUD) / "05-paidly.yaml", registry=registry)
    assert not spoken_mod.points_back(golden, AB)                     # off the chain: the registry's row, as before


def _item(**kw):
    base = dict(entry="x", key=PF, part=3, question="", options=(), escape="I can't tell", anchor=None, stem="",
                count_line=None, options_line="", escape_line="Or say you can't tell.", transform="none", under=None,
                over=None)
    base.update(kw)
    return cloud_mod.ComposedItem(**base)


def test_the_duration_bands_are_read_as_prices():
    six = tuple(friction_mod.labels(friction_mod.Duration(6, "WEEKS")).values())
    assert spoken_mod.duration_first_step(list(six)) == ["Under 6 weeks", "6 weeks to 3 months", "Over 3 months",
                                                         "It wouldn't be needed"]
    assert spoken_mod.side_question(list(six), 0) == "Under 2 weeks, or 2 to under 6 weeks?"
    assert spoken_mod.side_question(list(six), 3) == "3 to 6 months, or over 6 months?"
    one = tuple(friction_mod.labels(friction_mod.Duration(1, "WEEKS")).values())
    # 25-bidflow's served lines (keel-cloud 187 T009 table)
    assert spoken_mod.duration_first_step(list(one))[:3] == ["Under 1 week", "1 to 2 weeks", "Over 2 weeks"]
    assert spoken_mod.side_question(list(one), 0) == "Under 3 days, or 3 days to under 1 week?"
    stem = "If you bought Expanse, how long would a security review take before it went through?"
    clean = _item(question=stem, stem=stem, options=six, count_line="I'll read four options.",
                  options_line="Under 6 weeks; 6 weeks to 3 months; over 3 months; or it wouldn't be needed.",
                  transform="two_steps", under="Under 2 weeks, or 2 to under 6 weeks?",
                  over="3 to 6 months, or over 6 months?")
    reg = cloud_mod.registry_of_record(KEEL_CLOUD) if (KEEL_CLOUD / cloud_mod.REGISTRY_FILE).is_file() else None
    if reg is None:
        pytest.skip("no registry of record")
    assert spoken_mod.item_faults(clean, reg) == []
    assert any(f.startswith("S11") for f in spoken_mod.item_faults(_replace(clean, over="Over 3 months?"), reg))
    one_step = _replace(clean, transform="none", under=None, over=None)
    assert any(f.startswith("S9") for f in spoken_mod.item_faults(one_step, reg))
    six_read = _replace(clean, count_line="I'll read six options.")
    assert any(f.startswith("S7") for f in spoken_mod.item_faults(six_read, reg))
    three = tuple(spoken_mod.PURCHASE_ANSWERS.values())
    assert spoken_mod.transform_of(PF, list(three)) == "none" and spoken_mod.transform_of(PF, list(six)) == "two_steps"


def _replace(item, **kw):
    from dataclasses import replace                                     # noqa: PLC0415
    return replace(item, **kw)


def test_a_percent_first_step_is_held_to_its_shape(registry):
    six = ("Under 0.1%", "0.1% to under 0.25%", "0.25% to under 0.5%", "0.5% to under 1%", "1% or more",
           "I wouldn't pay for this")
    stem = "Palus takes a small fee on the balance. What fee a year would feel fair to you?"
    item = _item(key=PRICE, question=stem, stem=stem, options=six, escape="I can't say",
                 escape_line="Or say you can't say.", count_line="I'll read four options.",
                 options_line="Under a quarter of a percent; a quarter to under half a percent; half a percent or more; "
                              "or you wouldn't pay for this.", transform="two_steps",
                 under="Under a tenth of a percent, or a tenth to under a quarter of a percent?",
                 over="Half to under one percent, or one percent or more?")
    assert not [f for f in spoken_mod.item_faults(item, registry) if f.startswith(("S7", "S8", "S11"))]
    broken = _replace(item, options_line="A quarter; half; or you wouldn't pay for this.")
    assert any(f.startswith("S8") for f in spoken_mod.item_faults(broken, registry))


# ------------------------------------------------------------------------------- FR-8 the waiting state

def test_the_palus_waiting_state_is_never_a_scored_screen():
    """10-palus SOLUTION: screens 10 and 11 (`failed-solution-calibration`, the idea step's kicker and hint with no text)
    were scored R1 = 0, R2 = 0. A recorded bundle's `failed-*` screens are left out; the idea step (12) is read once."""
    fx = _fixture("10-palus-solution.json")
    names = [s["screen"] for s in fx["founder_screens"]]
    assert names.count("failed-solution-calibration") == 2 and names.count("idea") == 1
    bundle = {"founder_screens": fx["founder_screens"]}
    read = readers.founder_screens(bundle)
    assert [s.screen for s in read] == [n for n in names if not n.startswith("failed-")]
    assert [s.n for s in read] == [9, 12, 13]


def test_a_refused_job_is_evidence_named_by_its_reason_never_a_founder_screen():
    retried = inspect.getsource(cs._retried)
    assert "camera.founder(" not in retried and "evidence(" in retried and '"reason": reason' in retried
    cam = bt.Camera(run_dir=Path("/nonexistent"), page=None, watched={})
    assert cam.failure_shots == [] and callable(cam.evidence)
    assert '"failure_screens"' in inspect.getsource(bt)
    assert "IDEA_LINES_DRAWN" in inspect.getsource(vs_screens.Corridor.idea_check)
    assert "#idea-belief" in vs_screens.IDEA_LINES_DRAWN


def test_drift_97_counts_the_applied_jobs_and_names_the_retried_refusals():
    """Cycle 5's 10-palus and 13-aircaps SOLUTION stopped on DRIFT #97's count (*wire 6, script 4*): two RESULT_INVALID
    jobs Keel's AI wrote and the founder retried (spec 062) were counted as jobs chained. Applied jobs are held to the
    script; a refused one in scope must be one the walk retried."""
    fx = _fixture("10-palus-solution.json")
    rows = [{"screen": "CALIBRATION_QUESTIONS", "vector": v, "status": s, "created_at": str(n)}
            for n, (v, s) in enumerate(fx["calibration_jobs"])]
    findings = [{"what": "SOLUTION calibration", "refused": "RESULT_INVALID: L2", "reason": "RESULT_INVALID"}] * 2
    entry = SimpleNamespace(id="10-palus")

    def run(found):
        j = SimpleNamespace(recorder=_Recorder(), entry=entry, scope="SOLUTION", project_id="p", changed={},
                            findings=list(found), get=lambda path: rows)
        sj.drift_97(j)
        return j

    original = (vs.scope_vectors, vs.calibration_jobs)
    vs.scope_vectors = lambda e: ["SOLUTION"]
    vs.calibration_jobs = lambda e: [("SOLUTION", k) for k in range(4)]
    try:
        assert run(findings).changed["drift_97"]["refused_and_retried"] == {"SOLUTION": 2}
        with pytest.raises(AssertionError, match="refused and never retried"):
            run(findings[:1])
    finally:
        vs.scope_vectors, vs.calibration_jobs = original


# ------------------------------------------------------------- owed by keel-web 158 / 159 and keel-cloud 187

def test_the_ai_walk_answers_the_duration_bands_in_two_steps():
    """keel-web 158 (keel-cloud 187 FR-3): the duration bands are asked as Price's -- a band on a side said as step
    one's phrase, the side's two at `ai-sheet[data-ask=under|over]`; the middle band and *It wouldn't be needed* at
    once. The walk's ladder is the one Price's runs (`interviewer_leg._Walk.ladder`)."""
    fx = _fixture("10-palus-commercial.json")
    item = next(i for i in fx["interview"]["parts"][0]["items"] if i["dimension"] == PF)
    steps = vs.two_steps_of(item)
    assert steps["under"] == ["Under 2 weeks", "2 to under 4 weeks"] and steps["middle"] == "4 weeks to 3 months"
    assert steps["over_line"] == "3 to 6 months, or over 6 months?"
    assert vs.step_one(item, "2 to under 4 weeks") == ("Under 4 weeks", "under")
    assert vs.step_one(item, "Over 6 months") == ("over 3 months", "over")
    assert vs.step_one(item, "4 weeks to 3 months") == ("4 weeks to 3 months", None)
    assert vs.step_one(item, "It wouldn't be needed") == ("It wouldn't be needed", None)
    lock_before_187 = {**item, "spoken": {k: v for k, v in item["spoken"].items() if k not in ("under", "over")}}
    assert vs.step_one(lock_before_187, "Over 6 months") == ("Over 6 months", None)
    from evals import interviewer_leg as il                            # noqa: PLC0415
    assert "PRICE" not in inspect.getsource(il._Walk.price_in_two_steps), "any ladder served in two steps"


def test_the_send_heading_names_the_kinds_people_in_the_plural():
    """keel-web 159 FR-1 (`sendFormatTitle(label, labelShort)`): the long label first, by the lock step's plural."""
    from harness import interviewer_screens as ivs                     # noqa: PLC0415
    assert ivs.send_format_title("Startup founder", "founder") == "How should startup founders answer?"
    assert ivs.send_format_title("Startup founders", "startup founders") == "How should startup founders answer?"
    assert ivs.send_format_title("Someone who runs a payroll team") == "How should people who run a payroll team answer?"
    assert ivs.send_format_title(None, "founder") == "How should founders answer?"
    assert ivs.send_format_title(None) == "How should they answer?"


def test_the_check_screens_cap_is_the_served_one():
    """keel-cloud 187 FR-1 / keel-web 158 T006: Compatibility's items take 16 words; the Check intro says the served cap
    and a drafted row over it is cut to the served cap, never to a fixed nine."""
    assert vs_screens.served_word_cap({"saves": {"maxWords": 16}}) == 16
    assert vs_screens.served_word_cap({"saves": {}}) == vs_screens.served_word_cap(None) == 9
    assert vs_screens.check_intro_cap("Reword, remove or add; under 16 words each. You pick the one") == 16
    assert vs_screens.check_intro_cap("Pick the one.") is None
    assert "self._cut_over_cap_rows(name, served_word_cap(question))" in inspect.getsource(vs_screens.Corridor.list_check)
    assert "split()[:cap]" in inspect.getsource(vs_screens.Corridor._cut_over_cap_rows)
    assert "_hold_check_intro(j, question, seen[-1])" in inspect.getsource(cs)


def test_the_reader_pastes_the_duration_bands_amendment():
    """keel-cloud 187 FR-3 (guidelines §18): R6 reads the duration bands' second step against the rule that writes it."""
    assert readers.GUIDELINE_AMENDMENTS == ("16", "17", "18")
    guidelines = KEEL_CLOUD / readers.GUIDELINES_REL
    if not guidelines.is_file():
        pytest.skip("no guidelines in the keel-cloud checkout")
    assert "## 18. Amendment of 2026-11-01 (keel-cloud spec 187)" in guidelines.read_text(encoding="utf-8")
