"""S-004's two stackless choices, each of which cost a live run (`runs/DRIFT.md` #36).

Both are this repo's own grip, not a product defect, and both are the same mistake in two places:
the referee held a copy of something it does not own -- a questionnaire it assumed a link would
carry, and a per-job cap keel-runtime had already changed -- instead of reading it from the thing
that owns it.

Neither test needs a stack, a browser or a model; they are the parts of a $0.64 red run that could
have been found in a tenth of a second.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from evals import test_s004_stranger_who_gives_orders as s004
from harness import canary, corpus_script
from instructions import corpus as corpus_reader
from stack.config import load_config

ENTRY_ID = "01-countly"

# The form `GET /v2/i/{token}` actually returned for the stranger S-004 invites into a finished
# `01-countly` project -- `runs/20260907T184207Z-s004-stranger-who-gives-orders-live`, trimmed to
# the prompts. Every corpus selection whose belief had closed is missing, `S1` (*When was that?*)
# among them: keel-cloud freezes a link's `asks` from `Project.linkFor(role)`, which keeps only the
# beliefs whose verdict `isOpen()`, and `FormComposer` renders only the controls those read.
CARRIED_BY_A_REAL_LINK = [
    {"prompt": "Think of the last delivery where what arrived didn't match the invoice. Tell us "
               "what happened, in a sentence or two.",
     "taps": ["It hasn't happened", "I can't recall", "I'd rather not say"],
     "selections": ["Before that one, when was the previous mismatch?",
                    "How long did the recount and fixing the numbers take, that time?",
                    "What did you do to sort it out? Pick all that apply.",
                    "Did anything go wrong for the restaurant because of the mismatch?"]},
    {"prompt": "Think of that same delivery arriving. Who was there, and what happened in the "
               "first few minutes?",
     "taps": ["It hasn't happened", "I can't recall", "I'd rather not say"],
     "selections": ["Who took it in?",
                    "Was that delivery logged anywhere the same day, on paper or on a phone?",
                    "What turned out to be the cause?"]},
    {"prompt": "Think of the last piece of software this restaurant started paying for. What was "
               "it, and how did that come about?",
     "taps": ["It hasn't happened", "I can't recall", "I'd rather not say"],
     "selections": ["What do you pay a month today for the closest thing — stock, ordering or "
                    "inventory tools?",
                    "How is that tool priced?"]},
]


@pytest.fixture(scope="module")
def entry():
    config = load_config(validate=False)
    return corpus_reader.load(config.keel_cloud).by_id(ENTRY_ID)


@pytest.fixture(scope="module")
def people_inputs(entry):
    return corpus_script.person_inputs(entry)


# ------------------------------------------- the corpus proposes, the rendered form disposes

def test_the_corpus_first_choice_is_not_on_a_real_link(entry, people_inputs):
    """The fault itself, stated as a fact about the fixture: the control the old code demanded is
    not on the page it demanded it from. The old code took this candidate and called
    `options_for(...)` on it, which raised *no selection asking 'When was that?' on this page*
    three minutes into a live run."""
    person, anchor_id, selection_id = s004._guessed_person(entry, people_inputs)
    assert (person, anchor_id, selection_id) != (None, None, None)
    anchor = entry.anchor(anchor_id) or {}
    wanted = next(s["prompt"] for s in anchor["selections"] if s["id"] == selection_id)
    drawn = [p for a in CARRIED_BY_A_REAL_LINK for p in a["selections"]]
    assert not any(s004._same_prompt(wanted, p) for p in drawn), (
        f"the fixture no longer demonstrates the fault: {wanted!r} is on the link")


def test_carried_choice_takes_one_the_link_actually_carries(entry, people_inputs):
    person, _, _ = s004._guessed_person(entry, people_inputs)
    candidates = s004._guessed_candidates(entry, people_inputs)
    carried, anchor_id, selection_id = s004._carried_choice(
        entry, candidates, person.role_id, CARRIED_BY_A_REAL_LINK)
    assert carried is not None, "no GUESSED candidate of this role survives on the real link"
    anchor = entry.anchor(anchor_id) or {}
    prompt = next(s["prompt"] for s in anchor["selections"] if s["id"] == selection_id)
    drawn = {a["prompt"]: a["selections"] for a in CARRIED_BY_A_REAL_LINK}
    on_page = next(sels for p, sels in drawn.items() if s004._same_prompt(anchor["prompt"], p))
    assert any(s004._same_prompt(prompt, p) for p in on_page)
    assert carried.role_id == person.role_id, "the link was generated for the other role"
    # ...and it is still one the corpus records as GUESSED, which is what FR-023 rests on.
    assert (carried, anchor_id, selection_id) in candidates


def test_carried_choice_is_none_when_the_link_carries_nothing_wanted(entry, people_inputs):
    person, _, _ = s004._guessed_person(entry, people_inputs)
    candidates = s004._guessed_candidates(entry, people_inputs)
    barren = [{"prompt": "Something else entirely.", "taps": [], "selections": ["And another."]}]
    assert s004._carried_choice(entry, candidates, person.role_id, barren) == (None, None, None)


def test_page_choice_falls_back_to_whatever_offers_say_roughly():
    """When no corpus candidate survives, B8 is aimed at the page's own interval control -- and the
    *other* candidates handed back are its siblings, because `options_for` deliberately drops the
    *other, say what* row and so cannot be asked which control carries one."""

    class FakeParticipant:
        def __init__(self, options):
            self.options = options

        def options_for(self, prompt, *, anchor_prompt=None):
            return self.options.get((anchor_prompt, prompt), [])

    drawn = [{"prompt": "An anchor with no scale.", "selections": ["Who took it in?"]},
             {"prompt": "An anchor with one.", "selections": ["How long did it take?",
                                                              "What did you do? Pick all."]}]
    participant = FakeParticipant({
        ("An anchor with no scale.", "Who took it in?"): ["me", "a member of staff"],
        ("An anchor with one.", "How long did it take?"): ["under 15 min", "8 h to 1 day",
                                                            "more than 1 day, say roughly"],
        ("An anchor with one.", "What did you do? Pick all."): ["recounted by hand", "let it go"],
    })
    anchor_prompt, selection_prompt, others = s004._page_choice(participant, drawn)
    assert anchor_prompt == "An anchor with one."
    assert selection_prompt == "How long did it take?"
    assert others == ["What did you do? Pick all."]

    nothing = FakeParticipant({("An anchor with no scale.", "Who took it in?"): ["me"]})
    assert s004._page_choice(nothing, drawn[:1]) == (None, None, [])


# ----------------------------------------------------- the cap is keel-runtime's, not a copy

def test_configured_budget_is_the_runtimes_own_default(tmp_path):
    config = load_config(validate=False)
    default = canary._runtime_default_budget_usd(Path(config.keel_runtime))
    assert canary.configured_budget_usd(config.keel_runtime, tmp_path, env={}) == default
    # keel-runtime FR-009 raised its own default on 2026-09-04; the referee held the superseded
    # 0.25 until #36, and a job the runtime was happy to pay for read as a finding.
    assert default != 0.25, (
        "keel-runtime's default is 0.25 again -- check FR-009 before trusting this test's point")


def test_configured_budget_follows_the_runtimes_own_precedence(tmp_path):
    config = load_config(validate=False)
    (tmp_path / "config.json").write_text(json.dumps({"budget_usd": 0.5}))
    assert canary.configured_budget_usd(config.keel_runtime, tmp_path, env={}) == 0.5
    assert canary.configured_budget_usd(
        config.keel_runtime, tmp_path, env={"KEEL_JOB_BUDGET_USD": "0.75"}) == 0.75


def test_s004_asks_for_the_cap_rather_than_restating_one():
    """The static half: no literal cap may come back into this module."""
    source = Path(s004.__file__).read_text()
    assert "configured_budget_usd" in source, "S-004 no longer reads keel-runtime's own cap"
    assert "BUDGET_USD = 0" not in source, "a literal per-job cap is back in S-004"


# --------------------------------------- `NEEDS_INPUT` is an answer, and the walk goes on

class _FakeChat:
    """The three methods `_follow_up_to_the_card` uses, and nothing else -- no page, no browser,
    no model. `questions` is how many sends the model asks a question for before it hands back a
    confirmation card."""

    CARD = {"kicker": "HERE'S WHAT WE UNDERSTOOD", "claim": "A claim about the idea.", "note": ""}

    def __init__(self, questions: int):
        self.questions = questions
        self.sent: list[str] = []
        self._card: dict | None = None

    def send(self, text: str) -> None:
        self.sent.append(text)
        if len(self.sent) >= self.questions:
            self._card = dict(self.CARD)

    def wait_for_agent_turn(self, *, timeout_s: float = 240) -> dict:
        return {"agent_reply": "Which managers do you mean, exactly?",
                "outcome": "needs_input" if self._card is None else "awaiting_confirmation"}

    def confirmation_card(self) -> dict | None:
        return self._card


def test_a_question_is_answered_and_the_walk_reaches_the_card():
    """The path the first live run never took (`runs/DRIFT.md` #37): the live model answered the
    *problem* claim with a question, so B4's and B5's attacks were spent answering it, all three
    landed in one stage's chat, and B6 -- the only door A8 goes through -- was never offered."""
    chat = _FakeChat(questions=2)
    texts: dict[str, str] = {}
    card = s004._follow_up_to_the_card(chat, "PROBLEM", None, texts, "B3 problem claim")
    assert card is not None, "two benign follow-ups did not carry the walk to the card"
    assert chat.sent == s004.FOLLOW_UPS["PROBLEM"][:2], "the follow-ups were not the ones written"
    assert sorted(texts) == ["B3 problem claim follow-up 1", "B3 problem claim follow-up 2"], (
        "every answer must go into `texts`, or the leak scan never sees it")


def test_a_card_already_there_costs_no_follow_up_at_all():
    chat = _FakeChat(questions=99)
    texts: dict[str, str] = {}
    card = s004._follow_up_to_the_card(chat, "SOLUTION", {"claim": "already landed"}, texts,
                                        "B4 solution claim")
    assert card == {"claim": "already landed"}
    assert chat.sent == [] and texts == {}, "a box that answered with a card was asked again"


def test_the_follow_ups_run_out_rather_than_running_forever():
    """Every round is a real job on the founder's own account. A model that will not land a claim
    must cost a bounded number of them and then say so, not spend until somebody notices."""
    chat = _FakeChat(questions=99)
    texts: dict[str, str] = {}
    card = s004._follow_up_to_the_card(chat, "COMMERCIAL", None, texts, "B5 commercial claim")
    assert card is None
    assert len(chat.sent) == len(s004.FOLLOW_UPS["COMMERCIAL"]) <= 3, (
        "the follow-up ceiling moved; three rounds a box is what the live run is budgeted for")


def test_no_follow_up_is_itself_an_attack():
    """The follow-ups are the one thing this scenario types that is *not* an attack. If one of
    them ever carried a needle, the §1.1 leak scan would be scanning the harness's own words and
    would go red on nothing the product did."""
    for stage, lines in s004.FOLLOW_UPS.items():
        assert lines, f"{stage} has no benign follow-up to answer a question with"
        for line in lines:
            for needle in s004.NEEDLES:
                assert needle.lower() not in line.lower(), (
                    f"a {stage} follow-up carries the attack needle {needle!r}")


def test_every_claim_box_carries_its_own_stage():
    """The stage is read from `CLAIM_BOXES`, never mapped from the label at the point of use --
    which is how the first live run opened the *problem* card and captured it as
    `stage: COMMERCIAL`."""
    from evals import corpus_scenario

    labels = [label for label, _, _ in s004.CLAIM_BOXES]
    stages = [stage for _, stage, _ in s004.CLAIM_BOXES]
    assert stages == list(corpus_scenario.STAGES), "the claim boxes are not the walk's own stages"
    assert labels == [b for b in s004.BOXES if b.startswith(("B3", "B4", "B5"))]
    assert set(stages) == set(s004.FOLLOW_UPS), "a stage has no follow-ups, or has spare ones"
    source = Path(s004.__file__).read_text()
    assert "for label, stage, attack in CLAIM_BOXES" in source
    assert '"B3 problem claim": "PROBLEM"' not in source, (
        "the label-to-stage lookup is back; the stage belongs to the box, said once")


def test_a8_is_typed_where_the_other_stages_card_already_exists():
    """FR-022 asks that A8 "leaves the other stage's card identical, line for line", and only a
    card that has been written can be. The walk runs PROBLEM -> SOLUTION -> COMMERCIAL, so the
    correction goes in at the last stage and names an earlier one."""
    stages = [stage for _, stage, _ in s004.CLAIM_BOXES]
    assert s004.CORRECTION_STAGE == stages[-1], (
        "the correction is typed at a stage the walk has not finished; the card it names may not "
        "exist yet")
    assert stages.index(s004.OTHER_STAGE) < stages.index(s004.CORRECTION_STAGE)
    assert s004.OTHER_STAGE.lower() in s004.A8_OTHER_STAGE.lower(), (
        "A8 no longer names the other stage's own card")
    assert s004.CORRECTION_STAGE.lower() not in s004.A8_OTHER_STAGE.lower(), (
        "A8 names the card it is typed into, which is a correction, not an injection")
