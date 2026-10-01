"""A real story for every anchor the host wrote (spec 028, T010/T012/T020).

**Corpus-driven, not fixture-driven.** Every case below runs against the real
`03-lullaby.yaml` — the revised entry with two occasions per person — and the four anchor prompts
the host model actually wrote in matrix run **36895521843**. A fixture would have let the matcher
pass against prompts nobody has ever been asked, which is exactly how the filler survived four
scenarios and a nightly matrix.

The run's own four prompts are `RUN_36895521843` below, copied from transcript seq 88, and the
assertion that matters most in this file is one line: **the purchase story goes under the purchase
anchor**, which is what the old positional pass got wrong.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from harness import corpus_script as cs
from harness import stranger_stories as ss
from stack.config import load_config

#: The four anchors the host wrote in matrix run 36895521843 (transcript seq 88), in page order.
#: Sections, in the same order: *about the last night the baby cried*, *about checking an app during
#: a night waking*, *about the last baby app you bought*, *about a baby app you pay for now*.
RUN_36895521843 = (
    "Think of the last night your baby woke you by crying. Tell us what happened, in a sentence "
    "or two.",
    "Think of a time in the last year when you opened an app on your phone during a night waking "
    "with your baby. Tell us about it.",
    "Think of the last baby-related app you bought or subscribed to. Tell us who decided to buy it "
    "and who had to agree.",
    "Think of the baby-tracking or white-noise app you currently pay for. Tell us about how much "
    "you pay and how you pay for it.",
)

#: The ticks `_their_pick` decided on that run's own option lists, per anchor index (seq 110).
RUN_PICKS = {
    1: [("When was that?", "yes")],
    2: [("Who paid for that app?", "I did"),
        ("Did anyone else have to agree before you bought it?", "nobody")],
    3: [("Have you paid for a baby-tracking or white-noise app in the past year?", "yes"),
        ("How much do you pay per month?", "under £0.50"),
        ("How do you pay for it?", "a monthly subscription")],
}

JOURNEY = Path("evals/test_s012_journey_through_a_host.py")


@pytest.fixture(scope="module")
def keel_cloud():
    return load_config(validate=False).keel_cloud


@pytest.fixture(scope="module")
def lullaby(keel_cloud):
    return cs.entry_for(keel_cloud, "03-lullaby")[1]


@pytest.fixture(scope="module")
def every_entry(keel_cloud):
    return cs.load(keel_cloud).entries


# ---------------------------------------------------------------------------------- content words

def test_the_frames_own_four_words_are_dropped_because_every_prompt_carries_them():
    # keel-cloud's `questions.md` writes "Think of the last ... Tell us ..." into every anchor it
    # writes. A word in every prompt cannot tell two prompts apart.
    words = ss.content_words("Think of the last night. Tell us what happened, in a sentence or two.")
    assert "think" not in words and "tell" not in words and "sentence" not in words
    assert {"night", "happened"} <= words


def test_a_plural_matches_its_singular_and_two_letter_words_are_dropped():
    assert ss.content_words("apps and gadgets") == {"app", "gadget"}
    assert ss.content_words("it is an ad") == set()


def test_the_score_is_the_count_of_shared_content_words():
    assert ss.occasion_score("the baby app you bought", "the last app you bought") == 2
    assert ss.occasion_score("the baby app", "a payroll run") == 0


# ---------------------------------------------------------------------------------- the matcher

def test_the_run_matches_the_night_waking_and_the_purchase_to_their_own_anchors(lullaby):
    prompts = ss.corpus_prompts(lullaby)
    assert list(prompts) == ["A1", "A3"], "the revised entry carries two occasions, not four"
    matched = ss.match_occasions(RUN_36895521843, prompts)
    # This is the whole of the red run's misfiling, inverted: A3 is the purchase occasion and it
    # goes under the purchase anchor, not under "opened an app during a night waking".
    assert matched == {0: "A1", 1: None, 2: "A3", 3: None}


def test_the_purchase_story_would_have_gone_to_the_wrong_anchor_in_page_order(lullaby):
    """The bug, reproduced. A per-anchor greedy pass in page order gives the second anchor the
    purchase story, because its own best match was already spent (spec 028 FR-002, D-01)."""
    prompts = ss.corpus_prompts(lullaby)
    spent, positional = set(), {}
    for i, prompt in enumerate(RUN_36895521843):
        scores = {a: s for a, s in ss.scores_against(prompt, prompts).items()
                  if a not in spent and s >= ss.FLOOR}
        best = max(scores, key=lambda a: scores[a]) if scores else None
        positional[i] = best
        spent.add(best)
    assert positional[1] == "A3" and positional[2] is None
    assert ss.match_occasions(RUN_36895521843, prompts)[2] == "A3"


def test_the_match_is_global_best_first_whatever_order_the_host_wrote_them_in(lullaby):
    prompts = ss.corpus_prompts(lullaby)
    shuffled = (RUN_36895521843[2], RUN_36895521843[3], RUN_36895521843[0], RUN_36895521843[1])
    assert ss.match_occasions(shuffled, prompts) == {0: "A3", 1: None, 2: "A1", 3: None}


def test_no_corpus_occasion_is_spent_twice(lullaby):
    prompts = ss.corpus_prompts(lullaby)
    twice = RUN_36895521843 + RUN_36895521843
    matched = ss.match_occasions(twice, prompts)
    used = [a for a in matched.values() if a]
    assert sorted(used) == ["A1", "A3"], f"an occasion was asked twice: {matched}"


def test_the_floor_fails_closed_rather_than_matching_a_stranger_occasion(lullaby):
    prompts = ss.corpus_prompts(lullaby)
    assert ss.match_occasions(("Think of the last time you ran a payroll.",), prompts) == {0: None}
    # And raising the floor only ever loses a match -- never gains one.
    high = ss.match_occasions(RUN_36895521843, prompts, floor=99)
    assert set(high.values()) == {None}


def test_the_match_is_a_pure_function_and_ties_break_by_corpus_order(lullaby):
    prompts = ss.corpus_prompts(lullaby)
    once = ss.match_occasions(RUN_36895521843, prompts)
    assert once == ss.match_occasions(RUN_36895521843, prompts)
    tied = {"X1": "a baby app", "X2": "a baby app"}
    assert ss.match_occasions(("the baby app you bought",), tied) == {0: "X1"}


def test_every_entrys_own_occasions_match_themselves_and_nothing_else(every_entry):
    """Seven entries, each anchor prompt matched against its own entry's prompts. An entry whose
    occasions cannot tell each other apart would make the matcher a coin toss on that entry."""
    for entry in every_entry:
        prompts = ss.corpus_prompts(entry)
        if len(prompts) < 2:
            continue
        matched = ss.match_occasions(list(prompts.values()), prompts)
        want = {i: anchor for i, anchor in enumerate(prompts)}
        assert matched == want, f"{entry.id}: an occasion did not match itself -- {matched}"


# ------------------------------------------------------------------------------- when and thing

@pytest.mark.parametrize("story,want", [
    ("Last night. Up at one, half three and five.", "Last night"),
    ("Huckleberry, the sleep app, two months ago. I bought it.", "two months ago"),
    ("A white-noise machine, my wife ordered it in the spring.", "in the spring"),
    ("Wonder Weeks app, ages ago, I paid the one-off.", "ages ago"),
    ("Night before last. Three times.", "Night before last"),
    ("Wednesday. Twice.", "Wednesday"),
    ("A sound machine, I bought it on Prime Day.", "on Prime Day"),
    ("About ten days ago, once.", "About ten days ago"),
    ("A video monitor, my mum bought it when she was born.", "when she was born"),
    ("Most nights it's a few times, I honestly lose count.", None),
])
def test_the_when_is_the_storys_own_first_time_phrase(story, want):
    assert ss.when_in(story) == want


def test_a_when_is_lower_cased_for_the_middle_of_a_sentence_but_a_weekday_keeps_its_capital():
    assert ss.when_in_prose("Last night") == "last night"
    assert ss.when_in_prose("Wednesday") == "on Wednesday"
    assert ss.when_in_prose("on Prime Day") == "on Prime Day"
    assert ss.when_in_prose(None) is None


@pytest.mark.parametrize("story,want", [
    ("Huckleberry, the sleep app, two months ago. I bought it.", "Huckleberry, the sleep app"),
    ("A white-noise machine, my wife ordered it in the spring.", "A white-noise machine"),
    ("Baby Tracker, last month, I subscribed.", "Baby Tracker"),
    ("A video monitor, my mum bought it when she was born.", "A video monitor"),
    ("Last night. Up at one, half three and five.", None),
    ("Wednesday. Twice. She was hot.", None),
    ("", None),
])
def test_the_thing_is_the_first_fragment_exactly_when_it_is_not_a_when(story, want):
    assert ss.thing_in(story) == want


def test_an_article_loses_its_capital_in_the_middle_of_a_sentence_and_a_name_does_not():
    assert ss.thing_in_prose("A white-noise machine") == "a white-noise machine"
    assert ss.thing_in_prose("The sleep app") == "the sleep app"
    assert ss.thing_in_prose("Huckleberry, the sleep app") == "Huckleberry, the sleep app"
    assert ss.thing_in_prose("Baby Tracker") == "Baby Tracker"


def test_every_lullaby_purchase_story_names_a_thing_and_every_night_story_names_a_when(lullaby):
    for person in lullaby.people():
        a1 = (person.anchors.get("A1") or {}).get("text") or ""
        a3 = (person.anchors.get("A3") or {}).get("text") or ""
        if a1.strip() and (person.anchors["A1"].get("anchoring") == "ANCHORED"):
            assert ss.when_in(a1), f"{person.person}'s A1 carries no time phrase: {a1!r}"
        if a3.strip() and (person.anchors["A3"].get("anchoring") == "ANCHORED"):
            assert ss.thing_in(a3), f"{person.person}'s A3 names no thing: {a3!r}"


# ------------------------------------------------------------------------------- the composer

def test_the_lead_verb_comes_from_the_hosts_own_prompt():
    assert ss.lead_for(RUN_36895521843[2]) == ("Bought", False)
    assert ss.lead_for(RUN_36895521843[1]) == ("Opened", False)
    assert ss.lead_for(RUN_36895521843[3]) == ("Pay for", True)
    assert ss.lead_for("Think of the last time your team did the thing.") == (ss.LEAD_FALLBACK,
                                                                             False)


@pytest.mark.parametrize("prompt,value,want", [
    ("Who paid for that app?", "I did", "I paid for it myself"),
    ("Who paid for that app?", "me", "I paid for it myself"),
    ("Who paid for that app?", "my partner", "my partner paid for it"),
    ("Who paid for that app?", "a grandparent", "a grandparent paid for it"),
    ("Did anyone else have to agree?", "nobody", "nobody else had to agree"),
    ("How do you pay for it?", "a monthly subscription", "a monthly subscription"),
    ("How do you pay for it?", "one-off purchase", "a one-off purchase"),
    ("How much do you pay per month?", "under £0.50", "under £0.50 a month"),
    ("What did it cost?", "£5 to £10", "£5 to £10"),
    ("Was that recent?", "yes", None),
    ("Was that recent?", "no", None),
    ("How much?", "don't know", None),
    ("Where was the baby?", "cot in our room", "cot in our room"),
])
def test_a_value_becomes_a_clause_or_is_dropped_for_anchoring_nothing(prompt, value, want):
    assert ss.value_clause(prompt, value) == want


def test_a_money_bucket_keeps_its_own_edges_and_is_never_rounded():
    assert ss.value_clause("How much per month?", "£2 to £5") == "£2 to £5 a month"
    assert "2.5" not in (ss.value_clause("How much per month?", "£2 to £5") or "")


def test_the_composed_sentence_for_the_runs_purchase_anchor(lullaby):
    plans = ss.plan(RUN_36895521843, lullaby, "Amira Saleh", RUN_PICKS)
    assert plans[2].path == ss.THEIR_OWN_STORY
    assert plans[3].path == ss.COMPOSED
    assert plans[3].text == ("Pay for Huckleberry now, under £0.50 a month, "
                             "a monthly subscription.")


def test_the_composed_sentence_for_the_runs_app_opening_anchor(lullaby):
    plans = ss.plan(RUN_36895521843, lullaby, "Amira Saleh", RUN_PICKS)
    assert plans[1].path == ss.COMPOSED
    assert plans[1].text == "Opened Huckleberry, the sleep app, last night."
    # The thing is her own A3's and the when is her own A1's, and the record says so.
    assert (plans[1].thing_from, plans[1].when_from) == ("A3", "A1")


def test_a_composed_sentence_carries_no_word_that_is_not_the_persons_own_or_a_picked_value(lullaby):
    """FR-008, mechanically: every alphabetic word of a composed sentence is either in that
    person's own corpus stories, in a value this anchor is about to be given, or in the module's
    own small grammar vocabulary."""
    grammar = ss.content_words(" ".join(
        [lead for _, lead in ss.LEAD_VERBS] + [clause for _, clause in ss.VALUE_CLAUSES]
        + ["Pay for", ss.LEAD_FALLBACK, "now", "a month", "on"]))
    for person in lullaby.people():
        own = ss.content_words(" ".join((v or {}).get("text") or ""
                                        for v in person.anchors.values()))
        for plan in ss.plan(RUN_36895521843, lullaby, person.person, RUN_PICKS):
            if plan.path != ss.COMPOSED:
                continue
            picked = ss.content_words(" ".join(v for _, v in RUN_PICKS.get(plan.index) or ()))
            strays = ss.content_words(plan.text) - own - picked - grammar
            assert not strays, f"{person.person} [{plan.index}]: invented {strays} in {plan.text!r}"


def test_no_sentence_at_all_where_the_person_names_no_thing():
    assert ss.compose("Think of the last app you bought.", thing=None, when="last week") is None


def test_the_sentence_is_written_from_the_picks_so_the_two_cannot_disagree(lullaby):
    """FR-010: the same anchor, two different decided picks, two different sentences."""
    one = ss.plan(RUN_36895521843, lullaby, "Ben Carter",
                  {3: [("How much do you pay per month?", "under £0.50"),
                       ("How do you pay for it?", "a one-off purchase")]})[3]
    other = ss.plan(RUN_36895521843, lullaby, "Ben Carter",
                    {3: [("How much do you pay per month?", "£10 to £20"),
                         ("How do you pay for it?", "a monthly subscription")]})[3]
    assert one.text == "Pay for a white-noise machine now, under £0.50 a month, a one-off purchase."
    assert other.text == ("Pay for a white-noise machine now, £10 to £20 a month, "
                          "a monthly subscription.")


# ------------------------------------------------------------------------------- the three paths

def test_every_invited_lullaby_person_answers_every_anchor_and_none_of_them_guesses(lullaby):
    chosen, skipped = cs.people_to_invite(lullaby, 5)
    assert not skipped and len(chosen) == 5
    for person in chosen:
        plans = ss.plan(RUN_36895521843, lullaby, person.person, RUN_PICKS)
        assert len(plans) == 4
        assert all(p.path in (ss.THEIR_OWN_STORY, ss.COMPOSED) for p in plans), \
            f"{person.person} escaped an anchor they have facts for: {[p.path for p in plans]}"
        assert all((p.text or "").strip() for p in plans)
        assert all(p.tap is None for p in plans)


def test_two_of_the_four_are_their_own_words_and_two_are_composed(lullaby):
    for person in cs.people_to_invite(lullaby, 5)[0]:
        paths = [p.path for p in ss.plan(RUN_36895521843, lullaby, person.person, RUN_PICKS)]
        assert paths == [ss.THEIR_OWN_STORY, ss.COMPOSED, ss.THEIR_OWN_STORY, ss.COMPOSED]


def test_a_blank_corpus_anchor_with_a_tap_taps_it_rather_than_composing(lullaby):
    """Leo Martins is the only person in `03-lullaby` with a blank occasion, and he is twelfth --
    `people_to_invite(entry, 5)` never reaches him, so FR-014 is held here (D-07)."""
    plans = ss.plan(RUN_36895521843, lullaby, "Leo Martins", RUN_PICKS)
    assert plans[0].path == ss.ESCAPE and plans[0].tap == "HASNT_HAPPENED"
    assert plans[0].text is None
    assert plans[2].path == ss.THEIR_OWN_STORY


def test_a_guessed_story_lends_nothing_to_another_anchor_and_the_rest_escape(lullaby):
    """Keiko Tanaka's A3 is `GUESSED`. It is typed under its own anchor, because the corpus means
    it to be, and it lends no thing to anything else -- so the two composed anchors have nothing to
    be built from and tap the escape instead (FR-009, FR-015)."""
    plans = ss.plan(RUN_36895521843, lullaby, "Keiko Tanaka", RUN_PICKS)
    assert plans[2].path == ss.THEIR_OWN_STORY and plans[2].anchoring == "GUESSED"
    assert [p.path for p in plans] == [ss.THEIR_OWN_STORY, ss.ESCAPE, ss.THEIR_OWN_STORY,
                                       ss.ESCAPE]
    assert plans[1].tap == "CANT_RECALL" and plans[3].tap == "CANT_RECALL"


def test_the_record_says_which_path_and_where_every_part_came_from(lullaby):
    rows = ss.typed(ss.plan(RUN_36895521843, lullaby, "Amira Saleh", RUN_PICKS))
    assert [r["path"] for r in rows] == [ss.THEIR_OWN_STORY, ss.COMPOSED, ss.THEIR_OWN_STORY,
                                         ss.COMPOSED]
    assert rows[0]["corpus occasion"] == "A1" and rows[0]["the matcher's scores"] == {"A1": 5,
                                                                                     "A3": 2}
    composed = rows[3]
    assert composed["the thing, and whose occasion named it"] == ["Huckleberry, the sleep app",
                                                                  "A3"]
    assert composed["the picks it was written from"][1] == "How much do you pay per month? -> under £0.50"
    assert all(r["why"].strip() for r in rows)


def test_a_person_the_entry_does_not_name_is_refused_rather_than_guessed_at(lullaby):
    with pytest.raises(KeyError):
        ss.plan(RUN_36895521843, lullaby, "Nobody At All", RUN_PICKS)
# --------------------------------------------------------------------- the filler, proven dead

def test_the_filler_is_named_twice_in_the_journey_and_typed_nowhere():
    """FR-017: *a named, asserted-never-used constant.*

    Twice, and exactly twice: its own definition, and the §2.3 guard that fails the run if it ever
    reaches the page. A third reading means somebody reached for it again, which is the whole of
    run 36895521843.
    """
    source = JOURNEY.read_text()
    assert source.count("THE_STRANGER_SAYS") == 2, (
        "`THE_STRANGER_SAYS` is read somewhere other than its definition and its own never-used "
        "guard -- the filler is being typed again, and keel-cloud's INTERPRET reads it as a guess "
        "(spec 028, run 36895521843)")
    assert "I am thinking of the last time this happened to me" in source, (
        "the filler's own words are gone from the module -- keep them, with the reason, so the "
        "lesson is greppable (AGENTS.md: invert or move, never delete)")


def test_the_one_reading_of_the_filler_is_the_guard_that_it_never_reaches_the_page():
    body = JOURNEY.read_text().split("def _answer_whatever_is_asked", 1)[1].split("\ndef ", 1)[0]
    assert "fillers" in body and "THE_STRANGER_SAYS" in body
    # Never an argument to `tell_story`: the constant is compared against, never typed.
    for line in body.splitlines():
        if "tell_story" in line:
            assert "THE_STRANGER_SAYS" not in line, line


def test_the_journey_reads_the_module_and_no_longer_has_its_own_story_reader():
    source = JOURNEY.read_text()
    assert "stranger_stories" in source
    assert "def _story_texts" not in source, (
        "`_story_texts` handed out stories by position; `stranger_stories.plan` is now this "
        "repository's one reading of which words a stranger types")


def test_the_journey_decides_its_picks_before_it_tells_its_story():
    """FR-010 as a source order: within `_answer_whatever_is_asked`, the options are read and the
    ticks decided above the `tell_story` call, not below it."""
    body = JOURNEY.read_text().split("def _answer_whatever_is_asked", 1)[1].split("\ndef ", 1)[0]
    assert body.index("_their_pick(") < body.index("tell_story("), (
        "the story is typed before the picks are decided, so a composed sentence cannot be made "
        "to agree with them")
