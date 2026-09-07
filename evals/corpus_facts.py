"""The fact registry, derived from a corpus entry (spec 010 FR-011/FR-030, data-model.md §5).

One function -- `facts_for(entry)` -- so FR-015 holds: **the entry id is the only thing that
differs between the three scenario modules.** `evals/payroll_exceptions.py` uses it too, because
the smoke's fixture is corpus-shaped and goes through the same generator.

`evals/facts.Fact` is unchanged. What is new is that its `absent_hops`, which has existed unused
since spec 005, is finally scored (`harness/rubric.py`, policy v8 FR-030) -- and this module is
where the design's rule `Q5` and the mockup's own line become that check:

    "No line names your number or your answer. The band and the expected pick are yours; the
     people you ask never see them."

Three judgement calls are recorded here rather than discovered in a red run, because each is a
place where the obvious registry would have measured the wrong thing:

1. **What "the band" and "the expected pick" *are*, as text.** The naive reading is the raw
   numbers (`25`) and the raw option word (`recounted by hand`). Both would be **wrong to declare
   absent from the participant page**, and provably so: a bucket scale is *cut at the band's own
   edges* (that is `07-mulchrun`'s whole point -- *about 45 minutes* becomes `35…55`), and an
   expected option is, by definition, one of the options the person is offered. A registry that
   declared those absent would fail a product that is behaving exactly as designed.

   What is genuinely the founder's alone is the **marking**: keel-web writes the band as
   `you said 1 to 2` (`Strip.tsx`'s `composeBandLabel`) and the expected option as `{option} ✓`
   (`Chips.tsx`'s `.chip.expected`). Neither string can ever appear on a participant's page,
   because the participant page marks nothing. So those are the fact texts, and the absence check
   measures precisely what rule Q5 means.

2. **A band's positive hop is the opened card, not the review card.** data-model.md §5 puts it on
   `review_card`; the review card renders a band as *shaded chips* whose labels are keel-cloud's
   `BucketBuilder`'s, and recomputing those here would be a second builder -- the same mistake
   `research.md` R6 refused for the corpus reader. `Strip.tsx` is the one place keel-web composes
   a band into a sentence, and it lives on the opened card. The chips themselves are asserted by
   the scenario against the entry's own `expected.buckets` (FR-013), which is a stronger check
   than a FIDELITY substring would have been.

3. **A person's story reaches `answers_modal` only for the person whose modal is opened, and only
   for the anchor whose strip opened it.** A fact registered for a hop the run never visits is a
   check with nothing to check, not evidence of infidelity (policy v7's own note, learned on
   S-002's first green run, and re-learned here: `PersonAnswersModal` shows the story of the
   stage it was opened from, so a person's *other* stage's story is not on that screen and never
   was). So `facts_for` takes `modal_person=` and `modal_anchor=`.
"""

from __future__ import annotations

from evals.facts import Fact

# keel-web's own two markings, quoted from the source so a copy change here is a deliberate act:
# `Strip.tsx`'s `composeBandLabel`, and `Chips.tsx`'s expected-option tick (U+2713).
BAND_LEAD = "you said"
EXPECTED_TICK = "✓"

# Rule Q5's own hop: the founder's marking is absent from the stranger's page (FR-030).
NEVER_ON_THE_PARTICIPANT_PAGE = ["participant_page"]


def _number(value) -> str:
    """A bound's value as keel-web prints it -- JavaScript number formatting, which drops a
    trailing `.0` that Python would keep (`45.0` -> `45`)."""
    if isinstance(value, float) and value.is_integer():
        return str(int(value))
    return str(value)


def band_label(belief) -> str | None:
    """The founder's own band, as `Strip.tsx` composes it. `None` for a `CHOICE`, which has no
    band at all."""
    expectation = belief.expectation or {}
    if expectation.get("type") != "INTERVAL":
        return None
    lower = (expectation.get("lower") or {}).get("value")
    upper = (expectation.get("upper") or {}).get("value")
    if lower is not None and upper is not None:
        return f"{BAND_LEAD} {_number(lower)} to {_number(upper)}"
    if lower is not None:
        return f"{BAND_LEAD} {_number(lower)} or more"
    if upper is not None:
        return f"{BAND_LEAD} under {_number(upper)}"
    return BAND_LEAD


def expected_chip(belief) -> str | None:
    """The expected option as the founder's chip marks it -- `Chips.tsx`'s `{option} ✓`. `None`
    for an `INTERVAL`, which marks a band rather than a pick."""
    expectation = belief.expectation or {}
    if expectation.get("type") != "CHOICE":
        return None
    expected = expectation.get("expected")
    if not expected:
        return None
    return f"{expected} {EXPECTED_TICK}"


def facts_for(entry, *, modal_person: str | None = None,
              modal_anchor: str | None = None) -> dict[str, Fact]:
    """Every fact this entry's scenario traces, keyed by the readable ids of data-model.md §5.

    `modal_person` names the one person whose *answers modal* the scenario opens and
    `modal_anchor` the anchor whose strip opened it (judgement call 3); pass `None` for either
    when the scenario opens none.
    """
    facts: dict[str, Fact] = {
        "name": Fact(text=entry.title, kind="statement", hops=["stage_screen"]),
    }

    for stage, key in (("PROBLEM", "problem"), ("SOLUTION", "solution"),
                       ("COMMERCIAL", "commercial")):
        statement = (entry.statements or {}).get(key)
        if statement:
            facts[f"statement.{stage}"] = Fact(
                text=str(statement).strip(), kind="statement",
                hops=["review_card", "download"])

    # A `founderPhrase` that **is** one of its own belief's option words cannot be declared absent
    # from a page that must offer that option. `01-countly`'s `C17` is exactly that: the founder
    # said *per site*, and `S17` asks "How is that tool priced?" with `per site` among the four
    # answers. Design rule `Q5` forbids a *line* that names the founder's number or answer; it does
    # not forbid the option list from containing the word the founder happened to use, and it
    # could not -- the belief is about that word. Live-confirmed
    # (`runs/20260907T145804Z-s005-countly`, `FID-phrase.C17-participant_page-absent`).
    option_words = {str(option).strip().casefold()
                    for belief in entry.beliefs
                    for option in (belief.expectation or {}).get("options") or []}

    for belief in entry.beliefs:
        if belief.founder_phrase:
            # The founder's own precision word, beside the band (design §8.1 step 4). It is
            # quoted on the review card (`p.you-said`) and again on the opened card's strip
            # (`span.strip__you`) -- and it is the first thing rule Q5 forbids the stranger.
            collides = belief.founder_phrase.strip().casefold() in option_words
            facts[f"phrase.{belief.id}"] = Fact(
                text=belief.founder_phrase, kind="assumption",
                hops=["review_card", "opened_card"],
                absent_hops=[] if collides else list(NEVER_ON_THE_PARTICIPANT_PAGE))
        band = band_label(belief)
        if band:
            facts[f"band.{belief.id}"] = Fact(
                text=band, kind="assumption", hops=["opened_card"],
                absent_hops=list(NEVER_ON_THE_PARTICIPANT_PAGE))
        expected = expected_chip(belief)
        if expected:
            facts[f"expected.{belief.id}"] = Fact(
                text=expected, kind="assumption", hops=["review_card"],
                absent_hops=list(NEVER_ON_THE_PARTICIPANT_PAGE))

    for role in entry.roles or []:
        if role.get("label"):
            facts[f"role.{role['id']}"] = Fact(
                text=role["label"], kind="role", hops=["invite_screen"])

    for anchor in (entry.questionnaire or {}).get("anchors") or []:
        if anchor.get("prompt"):
            # The one story the stranger is asked. It is the anchor's own prompt on their page;
            # the opened card's `Asked: "…"` line quotes the *selection's* prompt, which is a
            # different string, so this fact does not claim that hop.
            facts[f"anchor.{anchor['id']}"] = Fact(
                text=" ".join(str(anchor["prompt"]).split()), kind="about_line",
                hops=["participant_page"])
        for selection in anchor.get("selections") or []:
            if selection.get("prompt"):
                facts[f"asked.{selection['id']}"] = Fact(
                    text=" ".join(str(selection["prompt"]).split()), kind="about_line",
                    hops=["participant_page", "opened_card"])

    for person in entry.people():
        slug = person.person.lower().replace(" ", "-")
        for anchor_id, written in person.written():
            hops = ["participant_page"]
            if (modal_person and person.person == modal_person
                    and (modal_anchor is None or anchor_id == modal_anchor)):
                hops.append("answers_modal")
            facts[f"said.{slug}.{anchor_id}"] = Fact(
                text=str(written.get("text")).strip(), kind="answer", hops=hops)
    return facts
