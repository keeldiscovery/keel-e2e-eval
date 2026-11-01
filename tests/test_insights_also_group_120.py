"""keel-web 155 FR-9 (keel-cloud 184 FR-8): a quote that answered a line's second stem is drawn under `alsoHeading`,
never in a group -- the matrix's s012 red of 2026-11-01 (Commitment's one quote, asked on the second stem, was expected in
`ol.rp-themes`). And 155 FR-7: the served `countLine` replaces the composed *Only k of the n* footer."""
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
    assert want["took_by"] == "None of the 1 were asked here: all 1 had already been asked about Importance."


def test_a_quote_on_the_first_stem_stays_in_its_group_and_the_composed_footer_holds_without_a_count_line():
    box = _box(countLine=None)
    box["themes"][0]["quotes"][0]["heading"] = "What would hold you back?"
    box["quotes"][0]["heading"] = "What would hold you back?"
    want = rm.expected_box(box)
    assert [t["label"] for t in want["themes"]] == [rm.fake.ON_THEIR_OWN_WORDS]
    assert want["also"] is None
    assert want["took_by"] == rm.fake.took_by(0, 1, box["tookBy"])
