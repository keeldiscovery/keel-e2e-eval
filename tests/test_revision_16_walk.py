"""Spec 068 (keel-cloud 129, keel-web 106): the harness half after revision 16, stackless -- contract 36's occasion on the
wire (FR-5), the spoken mirror's served escapes (FR-2), the moved people's lines (FR-3) and the reads of keel-web 106's
screens (FR-4). Pages are stubs; no browser, no stack."""

from __future__ import annotations

from contextlib import contextmanager
from types import SimpleNamespace

from harness import vectors_screens as vsc


# ------------------------------------------------------------------------------- FR-5: contract 36 on the wire

class _Request:
    def __init__(self, method: str, url: str, body):
        self.method, self.url, self.post_data_json = method, url, body


class _Response:
    def __init__(self, url: str, status: int, sent, body=None):
        self.url, self.status, self._body = url, status, body
        self.request = _Request("PUT", url, sent)

    def json(self):
        if self._body is None:
            raise ValueError("no body")
        return self._body


class _SavePage:
    """Just enough of a page for `Corridor._save_context`: the Save button and the PUT it answers."""

    def __init__(self, response: _Response):
        self.response, self.clicked = response, []

    @contextmanager
    def expect_response(self, predicate, timeout=0):
        assert predicate(self.response)
        yield SimpleNamespace(value=self.response)

    def get_by_role(self, role, name=None, exact=True):
        return SimpleNamespace(click=lambda: self.clicked.append(name))

    def on(self, *a):
        pass


def _corridor(page) -> vsc.Corridor:
    corridor = vsc.Corridor.__new__(vsc.Corridor)
    corridor.page, corridor.saves = page, []
    return corridor


def test_the_context_put_is_recorded_with_the_occasion_it_carried():
    """Contract 36 (keel-cloud 129 FR-11): the page sends `occasion` on the PUT once the founder's field holds one; the
    harness records the fields it sent and the occasion apart, and an older body (no occasion) reads None."""
    url = "http://localhost:18080/v2/projects/p1/context"
    sent = {"actor": "a", "job": "j", "circumstance": "c", "segment": "s",
            "recallWindow": {"count": 4, "unit": "WEEKS"}, "occasion": "delivery"}
    saved = _corridor(_SavePage(_Response(url, 202, sent, {"interaction_id": "i1"})))._save_context()
    assert saved["occasion"] == "delivery" and saved["sent"] == sent and saved["interaction_id"] == "i1"
    older = dict(sent)
    older.pop("occasion")
    saved = _corridor(_SavePage(_Response(url, 202, older, {"interaction_id": "i2"})))._save_context()
    assert saved["occasion"] is None and saved["sent"] == older
    refused = _corridor(_SavePage(_Response(url, 422, sent, {"code": "TEXT_REFUSED"})))._save_context()
    assert refused["status"] == 422 and refused["body"] == {"code": "TEXT_REFUSED"} and refused["occasion"] == "delivery"


# ------------------------------------------------------------------------------- FR-2: the served escapes

def test_issens_consumer_ability_item_names_the_served_escape_and_is_clean():
    """Spec 068 FR-2 (keel-cloud 129's owed list): Issen's 2026-10-23 host-door run served Ability to pay as the
    consumer budget item with *I can't say*; the guard read the registry's *I can't recall one* and called it RED.
    The escape a consumer Ability item names is the served one; the same item on a B2B link keeps the registry's."""
    from instructions import spoken as sp                               # noqa: PLC0415
    from instructions.cloud_corpus import ComposedItem                  # noqa: PLC0415
    from tests import v9_fixtures as fx                                 # noqa: PLC0415
    registry = fx.registry()
    stem = "Could you pay about $20 a month for this from money you already spend, or not?"
    item = ComposedItem(entry="11-issen", key="commercial.ability_to_pay", part=3, question=stem,
                        options=("From money I already spend on this", "From other money I'd set aside",
                                 "I couldn't pay it"),
                        escape="I can't say", anchor=None, stem=stem, count_line="I'll read three options.",
                        options_line="From money you already spend on this; from other money you'd set aside; or "
                                     "you couldn't pay it.",
                        escape_line="Or say you can't say.", transform="none")
    consumer = SimpleNamespace(chain=lambda: True, b2b=lambda: False, founder_list=lambda key: None)
    business = SimpleNamespace(chain=lambda: True, b2b=lambda: True, founder_list=lambda key: None)
    assert sp.item_escape(registry, "commercial.ability_to_pay", consumer) == "I can't say"
    assert sp.item_faults(item, registry, consumer) == []
    assert sp.item_escape(registry, "commercial.ability_to_pay", business) == \
        sp.registry_escape(registry, "commercial.ability_to_pay") == "I can't recall one"
    assert any(f.startswith("S6") for f in sp.item_faults(item, registry, business))


# ------------------------------------------------------------------------------- FR-3: the moved people's lines

def _backtest(entry_id: str):
    import pytest                                                       # noqa: PLC0415
    from pathlib import Path                                            # noqa: PLC0415
    from instructions import corpus as corpus_mod                       # noqa: PLC0415
    from stack.config import load_config                                # noqa: PLC0415
    from tests import v9_fixtures as fx                                 # noqa: PLC0415
    path = corpus_mod.backtest_dir(Path(load_config(validate=False).keel_cloud)) / f"{entry_id}.yaml"
    if not path.is_file():
        pytest.skip(f"no {entry_id} at {path.parent}")
    return corpus_mod.load_file(path, registry=fx.registry(), backtest=True)


def test_the_reader_keeps_the_people_the_revision_16_header_names():
    """129 FR-12: each back-test entry's header names the people whose Commitment pick moved; Issen's are the seven."""
    issen = _backtest("11-issen")
    assert issen.commitment_moved == ("Caleb Nguyen", "Jin-ho Park", "Farida Haque", "Imani Brooks", "Arjun Kapoor",
                                      "Tobias Wren", "Priya Natarajan")
    assert all((issen.person(n).picks or {}).get("commercial.commitment") == "yes_start"
               for n in issen.commitment_moved)


def test_a_header_naming_someone_else_or_an_unmoved_pick_is_refused(tmp_path):
    import pytest                                                       # noqa: PLC0415
    from instructions import corpus as corpus_mod                       # noqa: PLC0415
    from tests import v9_fixtures as fx                                 # noqa: PLC0415
    issen = _backtest("11-issen")
    text = issen.path.read_text(encoding="utf-8")
    stranger = tmp_path / "11-issen.yaml"
    stranger.write_text(text.replace("Changed: Caleb Nguyen,", "Changed: Nobody Here, Caleb Nguyen,", 1),
                        encoding="utf-8")
    with pytest.raises(corpus_mod.CorpusError, match="'Nobody Here' under Changed:, who is not one of its people"):
        corpus_mod.load_file(stranger, registry=fx.registry(), backtest=True)
    other = next(p.person for p in issen.people() if (p.picks or {}).get("commercial.commitment") == "no")
    unmoved = tmp_path / "x" / "11-issen.yaml"
    unmoved.parent.mkdir()
    unmoved.write_text(text.replace("Changed: Caleb Nguyen,", f"Changed: {other}, Caleb Nguyen,", 1), encoding="utf-8")
    with pytest.raises(corpus_mod.CorpusError, match="not yes_start"):
        corpus_mod.load_file(unmoved, registry=fx.registry(), backtest=True)


def test_a_moved_persons_line_for_the_second_yes_belongs_to_commitment_and_others_keep_theirs():
    """Spec 068 FR-3: Farida Haque's *I'd keep my weekly lesson and try the free sessions ...* was owed on Commitment by
    the r15 walk (her other answers owe nothing earlier), so it is Commitment's rung -- typed only on a Commitment
    follow-up, which her yes_start is never owed; Karsa's Bilal Qureshi's line was owed on an earlier rung and keeps
    it (a bare line, as revision 15 read it)."""
    from harness import interviewer_fake as fake                        # noqa: PLC0415
    from harness import vectors_script as vs                            # noqa: PLC0415
    issen = _backtest("11-issen")
    farida = next(p for p in vs.person_inputs(issen) if p.person == "Farida Haque")
    assert farida.follow_up_dimension == "commercial.commitment"
    assert fake.first_rung(farida.picks, vs.founder_side(issen), farida.link, b2b=vs.is_b2b(issen)) is None
    karsa = _backtest("09-karsa")
    bilal = next(p for p in vs.person_inputs(karsa) if p.person == "Bilal Qureshi")
    assert "Bilal Qureshi" in karsa.commitment_moved and bilal.follow_up_dimension is None
    assert not vs.moved_line_for_the_second_yes(karsa, bilal)


def test_a_second_yes_line_is_never_typed_and_the_walk_says_why():
    from evals import corpus_scenario as cs                             # noqa: PLC0415
    issen = _backtest("11-issen")
    j = SimpleNamespace(strict=False, entry=issen)
    farida = SimpleNamespace(person="Farida Haque")
    unasked = cs._moved_line(j, farida, "commercial.commitment", {}, None)
    assert "no follow-up was asked" in unasked["what"] and "spec 068 FR-3" in unasked["what"]
    # spec 075: the walk's follow-ups are a list (`follow_ups`), each with its own `did`
    elsewhere = cs._moved_line(j, farida, "commercial.commitment",
                               {"follow_ups": [{"did": "skipped", "line_for": "x"}]}, "commercial.price")
    assert "the server asked commercial.price" in elsewhere["what"]
    caleb = SimpleNamespace(person="Caleb Nguyen")
    typed = cs._moved_line(j, caleb, None, {"follow_ups": [{"did": "typed"}]}, "problem.current_solution_satisfaction")
    assert "was typed there" in typed["what"]
    assert cs._moved_line(SimpleNamespace(strict=True, entry=issen), farida, "commercial.commitment", {}, None) is None
    assert cs._moved_line(j, SimpleNamespace(person="Megan Ashford"), None, {}, None) is None


def test_the_follow_up_text_is_its_spoken_line_on_current_solution_and_relative_advantage():
    """keel-cloud 129 FR-3 (`FollowUpComposer.SAID_AS_SPOKEN`), mirrored where the harness composes the owed follow-up
    (S-006 and S-007 hold the route to it): Relative advantage's text no longer pastes the benefits."""
    from harness import interviewer_fake as fake                        # noqa: PLC0415
    from harness import vectors_script as vs                            # noqa: PLC0415
    # spec 086 FR-5 (keel-cloud 154): the rung names the idea and the job; spec 089 FR-4 (keel-cloud 159): on the scale's
    # last two, the occasion said
    assert fake.spoken_of("solution.relative_advantage", also=False) == \
        ("You said {solution_name} wouldn't make much difference on your last {occasion}. What would make {job} better "
         "for you, if anything?")
    # keel-cloud 131 FR-7 (spec 070 FR-2): Importance's text is its spoken line too
    assert set(vs.SAID_AS_SPOKEN) == {"problem.current_solution_satisfaction", "solution.relative_advantage",
                                      "problem.importance"}
    assert vs.had_no("Did you have a bank account in your own name that you could use?") == \
        "You said you had no bank account in your own name. What do you use instead?"
    assert vs.had_no("Was your phone within reach when the baby started crying?") is None


def test_paidlys_owed_relative_advantage_follow_up_reads_as_the_route_serves_it():
    """S-006 on the 129 build: the route said *You said it would not have made much difference. What would have?*; the
    harness composed *You said money in days, not weeks would have made no difference ...* (128's text). Since keel-cloud
    154 (spec 086 FR-5) the line names the idea and the job: the text is the filled spoken line."""
    from pathlib import Path                                            # noqa: PLC0415
    from harness import vectors_script as vs                            # noqa: PLC0415
    from instructions import corpus as corpus_mod                       # noqa: PLC0415
    from stack.config import load_config                                # noqa: PLC0415
    from tests import v9_fixtures as fx                                 # noqa: PLC0415
    keel_cloud = Path(load_config(validate=False).keel_cloud)
    paidly = corpus_mod.load_file(corpus_mod.corpus_dir(keel_cloud) / "05-paidly.yaml", registry=fx.registry())
    item = {"dimension": "solution.relative_advantage", "advantages": [{"label": "Money in days, not weeks"}],
            "options": []}
    interview = {"occasion": "invoice", "parts": [{"part": 2, "items": [item]}]}
    owed = vs.follow_up_question(paidly, [vs.Pick(dimension="solution.relative_advantage", codes=["no_difference"])],
                                 vs.LINK_PRIMARY, interview, "tok")
    assert owed["dimension"] == "solution.relative_advantage"
    # spec 089 FR-4 (keel-cloud 159 T011): the rung on the scale's last two, Paidly's occasion said
    assert owed["text"] == owed["spoken"] == ("You said invoice payout service wouldn't make much difference on your "
                                              "last invoice. What would make getting paid for finished work in time to "
                                              "cover the month better for you, if anything?")
    worse = vs.follow_up_question(paidly, [vs.Pick(dimension="solution.relative_advantage", codes=["worse"])],
                                  vs.LINK_PRIMARY, dict(interview, reveal={"what": "Imagine Paidly."}), "tok")
    assert worse["text"] == worse["spoken"] == "You said Paidly would have made things worse. What would have helped instead?"


# ------------------------------------------------------------------------------- FR-4: keel-web 106's screens

def test_a_consumer_reports_own_words_never_say_the_b2b_vocabulary_and_quotes_are_not_read():
    """keel-web 106 FR-2: tiles, leads, rows, the Insights boxes' words and the not-asked lines -- never a quote."""
    from evals import report_marks as rm                                # noqa: PLC0415
    board = {"tiles": {"price": {"text": "half or more said so · 9 of 13 decision-makers"}},
             "panels": {"COMMERCIAL": {"lead": "the payer would think it worth $20", "rows": [
                 {"key": "commercial.price", "text": "Price $20 to $29 a month per person"}]}}}
    insights = {"boxes": [{"key": "commercial.ability_to_pay", "head": "Ability to pay Did not hold",
                           "themes": [{"label": "would need new money", "quotes": ["“the payer is me” — Ann"]}]}],
                "not_asked": [{"key": "commercial.buyer_payer_alignment", "text": "No decision-maker was asked."}]}
    hits = rm.consumer_report_words(board, insights)
    assert sorted((h["where"], h["word"]) for h in hits) == [
        ("insight:commercial.ability_to_pay:theme", "new money"), ("lead:COMMERCIAL", "the payer"),
        ("not_asked:commercial.buyer_payer_alignment", "decision-maker"), ("row:commercial.price", "per person"),
        ("tile:price", "decision-makers")]
    assert rm.consumer_report_words({"tiles": {"price": {"text": "9 of 13 people"}}}, {}) == []


def test_a_bar_line_past_its_bar_reads_did_not_hold_with_no_split_and_guessed_words_are_apart():
    """keel-web 106 FR-3 / FR-4 on the Insights box (S-006 on the 129 build: Xavier Dubois, GUESSED, drawn apart)."""
    from evals import report_marks as rm                                # noqa: PLC0415
    from harness import interviewer_fake as fake                        # noqa: PLC0415
    quote = lambda who, iid: {"invitationId": iid, "name": who, "text": "One step too many."}  # noqa: E731
    insight = {"dimension": "solution.adoption_friction", "name": "Adoption friction", "status": "PEOPLE_DISAGREE",
               "state": "GROUPED", "themes": [{"label": "step", "count": 2,
                                               "quotes": [quote("Xavier Dubois", "x"), quote("Rosa Alvarez", "r")]}]}
    standings = {"vectors": [{"dimensions": [{"dimension": "solution.adoption_friction", "people": [
        {"invitationId": "x", "anchoring": "GUESSED"}, {"invitationId": "r", "anchoring": "ANCHORED"}]}]}]}
    guessed = rm.guessed_of(standings)
    assert guessed == frozenset({"x"})
    box = rm.expected_box(insight, {"n": 7}, guessed)
    assert box["head"] == ["Adoption friction", "Did not hold"] and box["split"] is None
    assert box["themes"][0]["count"] == 2 and len(box["themes"][0]["quotes"]) == 1
    assert box["guessed"] == [fake.quote_words(quote("Xavier Dubois", "x"))]
    held = dict(insight, dimension="commercial.purchase_friction", name="Purchase friction")
    fear = {"n": 6, "choice": {"optionCounts": [{"code": "yes_long", "count": 4}]}}
    assert rm.expected_box(held, fear)["head"][1] == "Holding up"
    assert rm.expected_box(dict(insight, dimension="problem.importance"))["split"] == fake.SPLIT_NOTE


def test_frequencys_card_counts_the_served_gates_units_where_a_gate_is_stored():
    """keel-cloud 129 FR-1 (`BriefFacts.card`, T003): S-006 on the 129 build read *the middle answer · days they waited
    beyond agreed terms to be paid for an approved invoice*; keel-cloud 130 FR-2 says it in the window's unit, *months*
    on Paidly's 3-month window (spec 069 FR-1); the corpus's reading (no stored gate) is unchanged."""
    from pathlib import Path                                            # noqa: PLC0415
    from harness import vectors_script as vs                            # noqa: PLC0415
    from instructions import brief_facts as bf                          # noqa: PLC0415
    from instructions import corpus as corpus_mod                       # noqa: PLC0415
    from stack.config import load_config                                # noqa: PLC0415
    from tests import v9_fixtures as fx                                 # noqa: PLC0415
    registry = fx.registry()
    paidly = corpus_mod.load_file(corpus_mod.corpus_dir(Path(load_config(validate=False).keel_cloud)) / "05-paidly.yaml",
                                  registry=registry)
    frequency = registry.by_key("problem.frequency")
    standing = {"status": "HOLDING_UP", "n": 10, "median": 2}
    assert bf.card(paidly, frequency, standing)["line"] == "the middle answer"
    assert bf.card(paidly, frequency, standing, clause=vs.event_past(paidly))["line"] == \
        "the middle answer · months they " + vs.event_past(paidly)


def test_the_follow_up_clips_may_carry_an_also_clip_beside_the_rung():
    """keel-cloud 118's #also clip (a rung's second stem) is not a rung: IM27 holds it beside the rung, DONE, and the
    backfill takes it out and stores it again (S-006 on the 129 build: six clips a role for five and four rungs)."""
    from evals import interviewer_marks as im                           # noqa: PLC0415
    from harness import interviewer_fake as fake                        # noqa: PLC0415
    want = ["solution.adoption_friction"]
    clip = {"itemId": "solution.adoption_friction", "status": "DONE",
            "script": fake.follow_up_script(fake.rung("solution.adoption_friction")[3])}
    also = {"itemId": "solution.adoption_friction#also", "status": "DONE",
            "script": "One more thing. What would make it clearly worth it to you?"}   # keel-cloud 144
    record = {"follow_up_clips": {"full": False, "roles": {"PRIMARY": {"want": want, "clips": [clip, also],
                                                                      "served": want}}}}
    ok, detail = im.the_follow_up_clips(record)
    assert ok, detail
    record["follow_up_clips"]["roles"]["PRIMARY"]["clips"] = [clip, dict(also, itemId="commercial.price#also")]
    assert not im.the_follow_up_clips(record)[0]


def test_the_name_box_opens_empty_with_no_suggestion_on_a_golden_walk_and_a_back_test_records_it():
    import pytest                                                       # noqa: PLC0415
    from evals import corpus_scenario as cs                             # noqa: PLC0415
    from harness.steps import Recorder                                  # noqa: PLC0415
    import tempfile                                                     # noqa: PLC0415
    recorder = Recorder(__import__("pathlib").Path(tempfile.mkdtemp()))
    founder = SimpleNamespace(solution_seed="A tag that whistles when you clap.")
    golden = SimpleNamespace(strict=True, entry=SimpleNamespace(id="03-lullaby"), founder=founder, recorder=recorder,
                             changed={}, findings=[])
    cs._hold_the_name_suggestion(golden, {"unnamed": {"value": ""}, "suggestion": None, "typed": "Whistle tag"})
    with pytest.raises(AssertionError):
        cs._hold_the_name_suggestion(golden, {"unnamed": {"value": ""}, "suggestion": "Use “Whistle”",
                                              "typed": "Whistle tag"})
    back = SimpleNamespace(strict=False, entry=SimpleNamespace(id="14-code-four"), founder=founder, recorder=recorder,
                           changed={}, findings=[])
    cs._hold_the_name_suggestion(back, {"unnamed": {"value": ""}, "suggestion": "Code Four", "typed": "Code Four"})
    assert back.changed["idea_name"]["suggestion"] == "Code Four" and "keel-web 106 FR-6" in back.findings[0]["what"]


def test_another_country_opens_on_its_own_currency_and_draws_the_served_line():
    import tempfile                                                     # noqa: PLC0415
    from pathlib import Path                                            # noqa: PLC0415
    from evals import corpus_scenario as cs                             # noqa: PLC0415
    from harness.steps import Recorder                                  # noqa: PLC0415
    line = "So the questions will be in English, in euros and cents, kilometres, metres and working days."
    j = SimpleNamespace(strict=False, entry=SimpleNamespace(id="21-codyco"), recorder=Recorder(Path(tempfile.mkdtemp())),
                        findings=[], changed={"market_other": {"country": "DE", "first_currency": "EUR", "line": line}})
    cs._hold_the_other_market(j)
    assert j.findings == []
    j.changed["market_other"] = {"country": "DE", "first_currency": "USD", "line": None}
    cs._hold_the_other_market(j)
    assert j.findings and "keel-web 106 FR-8" in j.findings[0]["what"]
    j.findings.clear()
    j.changed = {}
    cs._hold_the_other_market(j)
    assert j.findings == []


def test_the_friction_rows_columns_never_overlap():
    value = {"x": 16, "y": 100, "width": 180, "height": 40}
    assert not vsc.boxes_overlap(value, {"x": 200, "y": 100, "width": 150, "height": 60})
    assert not vsc.boxes_overlap(value, {"x": 16, "y": 140, "width": 300, "height": 20})   # wrapped under it
    assert vsc.boxes_overlap(value, {"x": 150, "y": 110, "width": 150, "height": 20})
    assert not vsc.boxes_overlap(None, value)


class _FieldPage:
    """A page with the context card's occasion field (or none), for `Corridor.context_occasion`."""

    def __init__(self, value: str | None):
        self.value = value

    def get_by_test_id(self, testid):
        return SimpleNamespace(count=lambda: int(self.value is not None and testid == "context-occasion"))

    def locator(self, selector):
        there = self.value is not None and selector == "input#context-occasion"
        node = SimpleNamespace(input_value=lambda: self.value)
        return SimpleNamespace(count=lambda: int(there), first=node)


def test_the_occasion_field_is_read_off_the_card():
    corridor = _corridor(_FieldPage("delivery"))
    assert corridor.context_occasion()["drawn"] is True and corridor.context_occasion()["value"] == "delivery"
    none = _corridor(_FieldPage(None)).context_occasion()
    assert none["drawn"] is False and none["value"] is None                    # spec 074: + `change`, `block`


def test_the_gates_no_is_the_served_no_label():
    """keel-cloud 129 FR-1 (`OccasionStem.noLabel`): where the gate asks a want the No reads *I didn't*; a gate drawn
    without the served No is a screen fault."""
    import inspect                                                      # noqa: PLC0415
    from evals import corpus_scenario as cs                             # noqa: PLC0415
    source = inspect.getsource(cs._hold_the_screens)
    assert 'served_gate.get("noLabel")' in source and '"gate No"' in source
