"""keel-web 155 FR-9 (keel-cloud 184 FR-8): a quote that answered a line's second stem is drawn under `alsoHeading`,
never in a group -- the matrix's s012 red of 2026-11-01 (Commitment's one quote, asked on the second stem, was expected in
`ol.rp-themes`). And 155 FR-7: the served `countLine` replaces the composed *Only k of the n* footer; since keel-web 258
FR-9 (spec 164 mirror 3) no footer is composed at all and `capped` is its own line."""
from evals import report_marks as rm


def _box(**over):
    q = {"invitationId": "11111111-1111-1111-1111-111111111111", "name": "Amira Saleh", "text": "A free trial first",
         "option": None, "side": "AGAINST", "heading": "What would you start with instead?"}
    box = {"dimension": "commercial.commitment", "name": "Commitment", "status": "TOO_FEW_TO_CALL", "state": "GROUPED",
           "rungHeading": "What would hold you back?", "alsoHeading": "What would you start with instead?",
           "asked": 0, "against": 1, "answered": 1, "skipped": 0, "tookBy": [{"dimension": "problem.importance",
           "name": "Importance", "count": 1}], "themes": [{"label": "ON_THEIR_OWN", "count": 1, "quotes": [q]}],
           "raw": False, "rawQuotes": [], "quotes": [q], "note": None, "dissent": False, "frame": None,
           "countLine": "None of the 1 were asked here: all 1 had already been asked about Importance."}
    box.update(over)
    return box


def test_a_quote_on_the_second_stem_is_expected_under_its_heading_not_in_a_group():
    want = rm.expected_box(_box())
    assert want["themes"] == []
    assert want["also"] == {"heading": "What would you start with instead?",
                            "quotes": ["\u201cA free trial first\u201d \u2014 Amira Saleh"]}
    assert want["count_line"] == "None of the 1 were asked here: all 1 had already been asked about Importance."
    assert want["capped"] is None                                    # no `capped` served (a recording before 270)


def test_a_quote_on_the_first_stem_stays_in_its_group_and_no_composed_footer_without_a_count_line():
    """Spec 164 mirror 3 (keel-web 258 FR-9): an older server's `tookBy` is read, never drawn -- no footer composed."""
    box = _box(countLine=None)
    box["themes"][0]["quotes"][0]["heading"] = "What would hold you back?"
    box["quotes"][0]["heading"] = "What would hold you back?"
    want = rm.expected_box(box)
    assert [t["label"] for t in want["themes"]] == [rm.fake.ON_THEIR_OWN_WORDS]
    assert want["also"] is None
    assert want["count_line"] is None and want["capped"] is None


def test_the_people_past_the_cap_are_their_own_line_unless_the_count_line_says_it():
    """Spec 164 mirror 3 (keel-web 258 FR-9, `insightsCapped`): *{k} of the {n} were past the two-question cap*."""
    box = _box(countLine=None, capped=2, against=5, asked=3)
    box.pop("tookBy")
    assert rm.expected_box(box)["capped"] == "2 of the 5 were past the two-question cap"
    assert rm.expected_box(_box(countLine=None, capped=1, against=4))["capped"] == "1 of the 4 was past the two-question cap"
    said = _box(countLine="3 of the 5 were asked here; 2 of the 5 were past the two-question cap", capped=2, against=5)
    assert rm.expected_box(said)["capped"] is None
    assert rm.expected_box(_box(countLine=None, capped=0))["capped"] is None
