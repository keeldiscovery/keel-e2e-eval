"""Policy v9 (`evals/policy.py` judgement call 12): `CLA-U5` stops sweeping a person's own words.

The check reads *no gendered pronoun in an element that renders a participant's name*, and the
download page renders both -- keel-web's `PrintRoute.tsx` draws an *In their words* block where a
participant's verbatim answer sits beside their name, so v8 read a person's own `his` as the
product writing it. v9 skips what the product renders as a **quotation of a participant**, keyed
on the structure keel-web marks one with, and keeps every other side of the check red.

Both sides are fixtured here, stacklessly, because a fix that only ever showed the quiet half
would be indistinguishable from deleting the check.
"""

from __future__ import annotations

from evals import policy
from harness import scoring
from harness.steps import Recorder

# One `.pquotes p`, exactly as the download page draws it: the participant's own words (the `<p>`'s
# own text nodes, curly quotation marks included) and their name in a child `<span>` beside them.
QUOTED = "“my supplier sends his invoices late, so I chase him every month”"
NAME = "Dana Okafor"
DOWNLOAD_TEXT = f"In their words {QUOTED} {NAME}"


def _checks_for(scorecard: dict, check_id: str) -> list[dict]:
    return [c for entry in scorecard["interactions"] for c in entry["checks"]
            if c["check_id"] == check_id]


def _score(tmp_path):
    return scoring.score_bundle(tmp_path, scenario="policy-v9", complete=True)


def test_the_version_is_nine():
    assert policy.POLICY_VERSION == 9


# ------------------------------------------------------- the quiet half: a quotation is not swept

def test_a_participants_own_pronoun_inside_a_quotation_does_not_fail_cla_u5(tmp_path):
    """The download page's own shape. Without v9 this is exactly the failure `## Discovered`
    recorded as the policy-9 candidate."""
    recorder = Recorder(tmp_path)
    with recorder.interaction("ui_visit"):
        with recorder.step("founder opens the download", party="founder", kind="browser") as h:
            h.capture_text("screen", "print")
            h.capture_text("download", DOWNLOAD_TEXT)
            h.capture_text("participant_names", NAME)
            h.capture_text("participant_quotes", QUOTED)

    checks = _checks_for(_score(tmp_path), "CLA-U5")
    assert len(checks) == 1
    assert checks[0]["pass"] is True
    assert "1 participant quotation not swept" in checks[0]["detail"]


def test_without_the_quotation_capture_the_same_page_still_fails(tmp_path):
    """The seam itself: the exemption is the *capture*, not a softer word list. A page that names
    a participant and never marked the words as a quotation is swept exactly as v6 swept it."""
    recorder = Recorder(tmp_path)
    with recorder.interaction("ui_visit"):
        with recorder.step("founder opens the download", party="founder", kind="browser") as h:
            h.capture_text("screen", "print")
            h.capture_text("download", DOWNLOAD_TEXT)
            h.capture_text("participant_names", NAME)

    checks = _checks_for(_score(tmp_path), "CLA-U5")
    assert len(checks) == 1
    assert checks[0]["pass"] is False
    assert "his" in checks[0]["detail"]


def test_the_said_boxs_quotation_is_exempt_too(tmp_path):
    """`SaidBox.tsx`'s `.said .w`, beside `.n` (the name) and `.r` (*Read as…*)."""
    quote = "“she usually calls me before the van leaves”"
    recorder = Recorder(tmp_path)
    with recorder.interaction("ui_visit"):
        with recorder.step("founder opens a dot", party="founder", kind="browser") as h:
            h.capture_text("screen", "opened_card")
            h.capture_text("opened_card",
                           f"{NAME} Restaurant manager {quote} Read as 1 to 2 h, anchored to "
                           "something that happened, so it counts")
            h.capture_text("participant_names", NAME)
            h.capture_text("participant_quotes", quote)

    checks = _checks_for(_score(tmp_path), "CLA-U5")
    assert len(checks) == 1
    assert checks[0]["pass"] is True


# --------------------------------------------- the loud half: product-authored text still fails

def test_product_authored_text_beside_a_name_still_fails_cla_u5(tmp_path):
    """The check's whole point, unchanged: the product describing a participant by gender. The
    page quotes somebody as well, so the exemption is live and this still goes red."""
    recorder = Recorder(tmp_path)
    with recorder.interaction("ui_visit"):
        with recorder.step("founder opens the download", party="founder", kind="browser") as h:
            h.capture_text("screen", "print")
            h.capture_text("download", f"{DOWNLOAD_TEXT} Her answers are in.")
            h.capture_text("participant_names", NAME)
            h.capture_text("participant_quotes", QUOTED)

    checks = _checks_for(_score(tmp_path), "CLA-U5")
    assert len(checks) == 1
    assert checks[0]["pass"] is False
    assert "her" in checks[0]["detail"]


def test_a_quotation_does_not_excuse_the_same_word_outside_it(tmp_path):
    """The removal is a literal substring anchored on the product's own quotation glyphs, so a
    one-word quotation cannot blow a hole in the sweep: *his* is removed where the page drew a
    quotation of it, and still found where the product wrote it in a sentence of its own."""
    recorder = Recorder(tmp_path)
    with recorder.interaction("ui_visit"):
        with recorder.step("founder opens the download", party="founder", kind="browser") as h:
            h.capture_text("screen", "print")
            h.capture_text("download",
                           f"In their words “his” {NAME}. We asked his manager too.")
            h.capture_text("participant_names", NAME)
            h.capture_text("participant_quotes", "“his”")

    checks = _checks_for(_score(tmp_path), "CLA-U5")
    assert len(checks) == 1
    assert checks[0]["pass"] is False
    assert "his" in checks[0]["detail"]


def test_cla_u5_is_still_skipped_where_no_participant_is_named(tmp_path):
    recorder = Recorder(tmp_path)
    with recorder.interaction("ui_visit"):
        with recorder.step("founder opens the stage card", party="founder", kind="browser") as h:
            h.capture_text("screen", "stage")
            h.capture_text("stage_screen", "Holding up.")

    assert _checks_for(_score(tmp_path), "CLA-U5") == []


# ------------------------------------------------ every other sweep still reads the quotations

def test_the_other_clarity_sweeps_are_untouched_by_the_exemption(tmp_path):
    """CLA-U1/U2/U4 read the whole captured screen, quotations and all. A raw enum is a leak
    wherever it renders, and no participant types `LOAD_BEARING` by accident."""
    quote = "“they marked it LOAD_BEARING and she signed it off”"
    recorder = Recorder(tmp_path)
    with recorder.interaction("ui_visit"):
        with recorder.step("founder opens the download", party="founder", kind="browser") as h:
            h.capture_text("screen", "print")
            h.capture_text("download", f"In their words {quote} {NAME}")
            h.capture_text("participant_names", NAME)
            h.capture_text("participant_quotes", quote)

    scorecard = _score(tmp_path)
    assert _checks_for(scorecard, "CLA-U5")[0]["pass"] is True
    assert _checks_for(scorecard, "CLA-U1")[0]["pass"] is False
    assert "LOAD_BEARING" in _checks_for(scorecard, "CLA-U1")[0]["detail"]


# -------------------------------------------------------------------- the helper's own edges

def test_a_blank_quotation_removes_nothing():
    """Removing an empty string would be removing everything; a capture that found no words is
    not evidence that the page quoted nobody."""
    assert policy.text_outside_quotations("her answers", ["", "   "]) == "her answers"
    assert policy.gendered_pronoun_violations(
        policy.text_outside_quotations("her answers", ["", "   "])) == ["her"]


def test_whitespace_is_collapsed_on_both_sides_before_the_removal():
    """`_SCREEN_TEXT_JS` collapses per text node; the quotation must match its own copy inside the
    whole screen's captured text character for character."""
    swept = policy.text_outside_quotations("In their words “his  van” Dana",
                                            ["“his van”"])
    assert policy.gendered_pronoun_violations(swept) == []


def test_the_key_the_capture_writes_is_the_key_the_policy_names():
    """One name, in one place -- `harness/browser.py` writes it and `harness/rubric.py` reads it
    through this constant, so a rename cannot leave the exemption silently dead."""
    assert policy.PARTICIPANT_QUOTE_KEYS == frozenset({"participant_quotes"})
