"""A real story for every anchor the host wrote (spec 028).

**The product was right and the stranger lied.** Matrix run 36895521843 got the live journey all
the way through -- three stages framed, the project's one questionnaire written, five people
invited, five answers read, the deck reached -- and then failed §1.7 because every one of the five
COMMERCIAL lines read `untested`. Nothing on the wire was wrong. The host wrote **four** anchors;
Lullaby's revised corpus carries **two** stories per person; and the harness typed a filler
sentence -- *"I am thinking of the last time this happened to me, and it went much the way I
described above."* -- under the other two. keel-cloud's INTERPRET reads that sentence for exactly
what it is: a guess. A guess is **shown and never counted** (`BeliefStanding.guessed`: *answers
shown to the founder that count towards nothing*), so the five commercial picks were made, stored,
and counted for nothing.

This module is the fix, and it is three pure functions and no browser:

1. **the matcher** -- which corpus occasion is the host's occasion, by what the two prompts are
   *about* rather than by the order they happen to be in. The order assumption is what put the
   corpus's app-purchase story under the host's *"opened an app during a night waking"* and left
   the host's *"the last baby app you bought"* holding the filler.
2. **the composer** -- for an anchor no corpus occasion matches, one anchored first-person sentence
   built from **that corpus person's own facts**: the thing their own story names, the when their
   own story carries, and the values of the picks the harness is about to tick on that very anchor.
   A story and a pick that disagree would be a worse stranger than a guessing one, so the picks are
   decided first and the sentence is written from them.
3. **the escape** -- where the corpus says this person has nothing for an occasion (a blank anchor
   with a tap), the escape is tapped. *It hasn't happened* is an honest answer that keel-cloud
   counts as one; a guess is not.

**Nothing here invents a fact.** Every word of a composed sentence comes from the corpus person's
own story text, or from a value the page itself offered and the harness is about to tick. The one
thing this module supplies is grammar -- a lead verb and a comma -- and the tables that supply it
are small, explicit and keyed on the *host's own words* or the *shape of a value*, never on a
corpus entry's name. `plan()` records, per anchor, which of the three paths it took and where each
part came from, so the bundle answers *whose words were those* without re-deriving anything.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Iterable, Mapping, Sequence

from instructions.context import tap_enum

# --------------------------------------------------------------------------------- the three paths

#: This person's own corpus story, typed under the anchor the matcher gave it.
THEIR_OWN_STORY = "their own story"
#: No corpus occasion matched this anchor, so one was composed from this person's own facts.
COMPOSED = "composed from their own facts"
#: The corpus says this person has nothing for this occasion, so the escape was tapped.
ESCAPE = "the escape, tapped"

PATHS = (THEIR_OWN_STORY, COMPOSED, ESCAPE)


# ------------------------------------------------------------------------------------ the matcher

#: Function words, and the four that keel-cloud's own `questions.md` frame puts in **every** anchor
#: prompt it writes (*"Think of the last ... Tell us ..."*). They are dropped because a word every
#: prompt carries cannot tell two prompts apart, and leaving them in makes every pair score the
#: same three points before anything about the occasion is compared at all.
STOPWORDS = frozenset("""
a about an and any are as at be been before but by can could did do does for from had has have
how i if in into is it its me my of on or our over so some tell that the their them then there
these they this those to told two us was we were what when where which who whom why will with
would you your yours think thinking sentence sentences please describe tell_us
""".split())

#: What the matcher calls close enough. Two content words in common is the floor: *app* and *baby*
#: alone is a weak match and the only thing a weak match can cost is a composed sentence in place
#: of a story, which is the safe direction to be wrong in. Below it the anchor is composed for,
#: which is honest; above it a story could be typed under an occasion it is not about, which is the
#: mistake this whole module exists to stop.
FLOOR = 2


def content_words(text: str) -> set[str]:
    """The words of a prompt that say what it is **about**, lower-cased and crudely singularised.

    Crude on purpose: a stemmer is a dependency and a surprise, and the only thing this has to do
    is let *apps* match *app* and *nights* match *night*. A trailing *s* comes off any token over
    three characters that does not end in *ss*, which mangles a few words identically on both sides
    of a comparison and therefore changes no score. Tokens shorter than three characters are dropped
    with the stopwords -- *"it"*, *"us"*, *"an"* -- because a two-letter word in common says nothing.
    """
    out = set()
    for raw in re.findall(r"[a-z0-9']+", (text or "").lower()):
        word = raw.strip("'")
        if len(word) < 3 or word in STOPWORDS:
            continue
        if len(word) > 3 and word.endswith("s") and not word.endswith("ss"):
            word = word[:-1]
        out.add(word)
    return out


def occasion_score(one: str, other: str) -> int:
    """How many content words two prompts share -- the whole of the matcher's judgement.

    Deliberately a count and not a ratio. A ratio would reward a short prompt for being short, and
    the host's prompts are long by instruction (keel-cloud `questions.md`: the qualifiers go in the
    anchor's prompt). What matters is how much of the *occasion* the two name in common.
    """
    return len(content_words(one) & content_words(other))


def match_occasions(host_prompts: Sequence[str], corpus_prompts: Mapping[str, str],
                    *, floor: int = FLOOR) -> dict[int, str | None]:
    """Which corpus occasion each host anchor is about: `{host index -> corpus anchor id | None}`.

    **Globally best first, not first-come-first-served.** A pass that walked the host's anchors in
    order and gave each one its own best remaining corpus occasion is how run 36895521843 put the
    app-purchase story under *"opened an app during a night waking"*: that anchor's best match was
    the night-waking occasion, which the first anchor had already taken, so it took what was left.
    This takes the highest-scoring pair anywhere in the grid, retires both sides, and repeats --
    so the night-waking story goes to the night-waking anchor and the purchase story to the
    purchase anchor, whatever order the host wrote them in.

    Every corpus occasion is spent at most once, and so is every host anchor: one occasion is asked
    once (`one-occasion-once-design.md` §8.2), and typing one story twice would be the same lie in
    a new place. Ties break by corpus order then host order, so the mapping is a pure function of
    its inputs and a run is reproducible from the bundle.
    """
    pairs = []
    for i, prompt in enumerate(host_prompts):
        for rank, (anchor_id, corpus_prompt) in enumerate(corpus_prompts.items()):
            score = occasion_score(prompt, corpus_prompt)
            if score >= floor:
                pairs.append((-score, rank, i, anchor_id))
    matched: dict[int, str | None] = {i: None for i in range(len(host_prompts))}
    spent: set[str] = set()
    for _, _, i, anchor_id in sorted(pairs):
        if matched[i] is None and anchor_id not in spent:
            matched[i] = anchor_id
            spent.add(anchor_id)
    return matched


def scores_against(host_prompt: str, corpus_prompts: Mapping[str, str]) -> dict[str, int]:
    """Every corpus occasion's score for one host anchor -- the matcher's own arithmetic, for the
    bundle. A reader who disagrees with a match can see what it was chosen over."""
    return {anchor_id: occasion_score(host_prompt, prompt)
            for anchor_id, prompt in corpus_prompts.items()}


# ----------------------------------------------------------------------------------- the when

#: Weekday and season words that keep their capital when a *when* is lower-cased into the middle of
#: a sentence. Everything else -- *Last night*, *Two months ago* -- is ordinary prose.
KEEP_CAPITAL = ("monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday",
                "prime day")

_NUMBER = r"(?:a|an|one|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve|a few|a couple of|\d+)"

#: The time phrases a corpus story actually uses. Read off all seven entries' `answers:` blocks
#: rather than imagined: *"Last night"*, *"two months ago"*, *"ages ago"*, *"in the spring"*,
#: *"Wednesday"*, *"Night before last"*, *"last month"*, *"on Prime Day"*, *"when she was born"*.
#: A story with none of these supplies no *when*, which `plan()` records rather than papering over.
WHEN_PATTERNS = tuple(re.compile(p, re.IGNORECASE) for p in (
    r"\bnight before last\b",
    r"\b(?:last|this|next)\s+(?:night|week|month|year|spring|summer|autumn|winter|"
    r"monday|tuesday|wednesday|thursday|friday|saturday|sunday)\b",
    rf"\b(?:about\s+)?{_NUMBER}\s+(?:day|days|week|weeks|month|months|year|years)\s+ago\b",
    r"\b(?:ages|a while|a long time|a bit)\s+ago\b",
    r"\b(?:yesterday|today|tonight|this morning|this afternoon|last thing)\b",
    r"\bin the (?:spring|summer|autumn|winter)\b",
    r"\bon prime day\b",
    r"\bwhen (?:she|he|they) (?:was|were) born\b",
    rf"\bin the last {_NUMBER}\s+(?:day|days|week|weeks|month|months|year|years)\b",
    r"\b(?:monday|tuesday|wednesday|thursday|friday|saturday|sunday)\b",
))


def when_in(text: str) -> str | None:
    """The first time phrase this story carries, in the story's own words, or `None`.

    *The first*, by position in the text and not by which pattern matched, because a story's own
    first time phrase is the one it is anchored to: Amira's A1 story opens *"Last night."* and that
    is when it happened.
    """
    best: tuple[int, str] | None = None
    for pattern in WHEN_PATTERNS:
        m = pattern.search(text or "")
        if m and (best is None or m.start() < best[0]):
            best = (m.start(), m.group(0))
    return best[1] if best else None


#: A *when* that already begins with its own preposition needs no comma in front of it: *"bought
#: it in the spring"*, *"opened it on Wednesday"*. Everything else is an adverbial that does --
#: *"bought it, two months ago"*.
_CARRIES_ITS_OWN_PREPOSITION = ("in ", "on ", "when ")
_WEEKDAYS = KEEP_CAPITAL[:7]


def when_in_prose(when: str | None) -> str | None:
    """A *when* ready to sit mid-sentence: lower-cased, except for the weekday and season names
    that are proper nouns whatever position they are in, and given its own *on* where it is a bare
    weekday (*"Wednesday"* -> *"on Wednesday"*)."""
    if not when:
        return None
    out = " ".join(when.lower().split())
    for word in KEEP_CAPITAL:
        out = re.sub(rf"\b{re.escape(word)}\b", word.title(), out)
    if out.casefold() in _WEEKDAYS:
        out = f"on {out}"
    return out


# ------------------------------------------------------------------------------------ the thing

_APPOSITION = ("the ", "a ", "an ")
#: An article keeps its capital at the head of a corpus story (*"A white-noise machine, ..."*) and
#: loses it in the middle of a composed sentence (*"Bought a white-noise machine ..."*). A product
#: name never does: *"Huckleberry"*, *"Baby Tracker"*, *"Wonder Weeks app"*.
_ARTICLES = ("a", "an", "the")


def thing_in_prose(thing: str | None) -> str | None:
    """The thing, ready to sit after a lead verb: an opening article lower-cased, a name left
    exactly as the corpus person wrote it."""
    if not thing:
        return None
    first, _, rest = thing.partition(" ")
    if first.casefold() in _ARTICLES and rest:
        return f"{first.lower()} {rest}"
    return thing


def thing_in(story: str) -> str | None:
    """The thing this story names -- *"Huckleberry, the sleep app"*, *"A white-noise machine"* --
    or `None` where it names an occasion rather than a thing.

    **The rule is the corpus's own register, not a parser.** Every purchase story in every entry
    opens with what was bought: *"Huckleberry, the sleep app, two months ago. I bought it."*,
    *"A white-noise machine, my wife ordered it in the spring."*, *"Baby Tracker, last month, I
    subscribed."* Every occasion story opens with when it happened: *"Last night."*, *"Night before
    last."*, *"Wednesday."* So the first fragment is the thing exactly when it is not a *when*, and
    the second fragment joins it when it is an apposition naming the same thing (*"the sleep app"*)
    rather than a time or a clause about a person.
    """
    fragments = [f.strip() for f in re.split(r"[.;,]", story or "") if f.strip()]
    if not fragments or when_in(fragments[0]):
        return None
    thing = fragments[0]
    if len(fragments) > 1:
        nxt = fragments[1]
        if nxt.lower().startswith(_APPOSITION) and not when_in(nxt):
            thing = f"{thing}, {nxt}"
    return thing


# ------------------------------------------------------------------------------- the composer

#: Which verb opens a composed sentence, chosen by a word in **the host's own prompt**. First match
#: wins, so the purchase row is tested before the opening-an-app row: *"the last baby-related app
#: you bought or subscribed to"* is a purchase whatever else it says.
LEAD_VERBS: tuple[tuple[frozenset[str], str], ...] = (
    (frozenset({"bought", "buy", "purchased", "purchase", "subscribed", "subscription", "paid"}),
     "Bought"),
    (frozenset({"opened", "open", "checked", "check", "used", "use", "reached"}), "Opened"),
)

#: A present-tense occasion -- *"the app you currently pay for"* -- is led differently and takes no
#: *when*: the fact is that it is being paid for now.
PRESENT_MARKERS = ("currently", "right now", "at the moment", "these days", "you now pay",
                   "do you now")

#: The fallback lead. A concrete past event with a *what* and a *when* and no verb of its own is
#: still an occasion, and this is the sentence that says so without claiming an action the host's
#: prompt never named.
LEAD_FALLBACK = "It was"

#: A bare *yes* or *no* anchors nothing: it is the answer to a question the stranger's sentence
#: cannot repeat without parroting the model's own words, and a sentence that says "yes" says
#: nothing about an occasion. Dropped from a composed sentence, and still ticked on the page.
NO_ANCHOR_IN_A_VALUE = frozenset({"yes", "no", "none", "don't know", "dont know", "can't recall",
                                  "cant recall", "rather not say", "don't use one"})

#: A picked value, turned into a clause. Keyed on the **shape of the value** -- who paid, nobody
#: else, free -- and never on a corpus entry, so the table is the same seven rows for all seven
#: entries and a value it does not know is used verbatim, which is the honest default.
VALUE_CLAUSES: tuple[tuple[frozenset[str], str], ...] = (
    (frozenset({"me", "i did", "i paid", "myself", "i bought it"}), "I paid for it myself"),
    (frozenset({"my partner", "my wife", "my husband", "partner"}), "my partner paid for it"),
    (frozenset({"a grandparent", "my mum", "my mother", "grandparent"}),
     "a grandparent paid for it"),
    (frozenset({"nobody", "no one", "nobody else", "no-one"}), "nobody else had to agree"),
    (frozenset({"it was free", "free"}), "it was free"),
    (frozenset({"a monthly subscription", "monthly subscription"}), "a monthly subscription"),
    (frozenset({"a one-off purchase", "one-off purchase", "one off purchase"}),
     "a one-off purchase"),
)

_MONEY = re.compile(r"[£$€]")
_PER_MONTH = re.compile(r"\b(?:per month|a month|monthly|each month)\b", re.IGNORECASE)


def lead_for(host_prompt: str) -> tuple[str, bool]:
    """`(lead, present_tense)` for one host anchor, off the host's own words."""
    low = (host_prompt or "").lower()
    if any(marker in low for marker in PRESENT_MARKERS):
        return "Pay for", True
    words = content_words(host_prompt)
    for markers, lead in LEAD_VERBS:
        if words & markers:
            return lead, False
    return LEAD_FALLBACK, False


def value_clause(selection_prompt: str, value: str) -> str | None:
    """One picked value as a clause, or `None` where the value anchors nothing.

    A money bucket keeps its own edges -- *"under £0.50"*, *"£5 to £10"* -- and gains *a month*
    only when the selection it answers asked per month. Rounding a bucket to a number would be
    inventing a figure the person never gave, which is the corpus's own rule (`Pick.roughly` is
    left `None` by every deterministic scenario for exactly this reason).
    """
    text = " ".join((value or "").split())
    if not text:
        return None
    key = text.casefold()
    if key in NO_ANCHOR_IN_A_VALUE:
        return None
    for markers, clause in VALUE_CLAUSES:
        if key in markers:
            return clause
    if _MONEY.search(text):
        return f"{text} a month" if _PER_MONTH.search(selection_prompt or "") else text
    return text


def compose(host_prompt: str, *, thing: str | None, when: str | None,
            values: Sequence[tuple[str, str]] = ()) -> str | None:
    """One anchored first-person sentence, or `None` where there is nothing honest to say.

    `values` are `(selection prompt, value)` pairs for **this anchor's own selections**, in the
    order the page draws them and already decided -- the very ticks the harness is about to make.
    That ordering is the point: a sentence written before the picks are chosen can disagree with
    them, and a stranger whose story contradicts their own answers is a worse witness than one who
    guesses.
    """
    if not thing:
        return None
    lead, present = lead_for(host_prompt)
    shown_thing = thing_in_prose(thing)
    if present:
        # A present-tense occasion takes the thing's **name** and not its apposition: *"Pay for
        # Huckleberry now"* rather than *"Pay for Huckleberry, the sleep app now"*, which needs a
        # comma the sentence then has to spend on the picks.
        head = f"{lead} {shown_thing.split(',')[0].strip()} now"
    else:
        shown = when_in_prose(when)
        if not shown:
            head = f"{lead} {shown_thing}"
        elif shown.lower().startswith(_CARRIES_ITS_OWN_PREPOSITION):
            head = f"{lead} {shown_thing} {shown}"
        else:
            head = f"{lead} {shown_thing}, {shown}"
    clauses = [c for c in (value_clause(prompt, value) for prompt, value in values) if c]
    seen, kept = set(), []
    for clause in clauses:
        if clause.casefold() not in seen:
            seen.add(clause.casefold())
            kept.append(clause)
    return f"{head}, {', '.join(kept)}." if kept else f"{head}."


# --------------------------------------------------------------------------------------- the plan

@dataclass(frozen=True)
class AnchorPlan:
    """What this stranger does with one anchor the host wrote, and where every word came from."""

    index: int
    host_prompt: str
    path: str
    text: str | None = None
    tap: str | None = None
    corpus_anchor: str | None = None
    anchoring: str | None = None
    scores: dict[str, int] = field(default_factory=dict)
    thing: str | None = None
    thing_from: str | None = None
    when: str | None = None
    when_from: str | None = None
    values_used: tuple[str, ...] = ()
    why: str = ""

    def recorded(self) -> dict:
        """The row this anchor contributes to the bundle (`§2.3`'s own record)."""
        out = {
            "anchor": self.host_prompt[:60],
            "path": self.path,
            "said": (self.text or "")[:200] or None,
            "tapped": self.tap,
            "why": self.why,
            "the matcher's scores": self.scores,
        }
        if self.corpus_anchor:
            out["corpus occasion"] = self.corpus_anchor
            out["the corpus's own anchoring"] = self.anchoring
        if self.path == COMPOSED:
            out["the thing, and whose occasion named it"] = [self.thing, self.thing_from]
            out["the when, and whose occasion carried it"] = [self.when, self.when_from]
            out["the picks it was written from"] = list(self.values_used)
        return out


def corpus_prompts(entry) -> dict[str, str]:
    """`{anchor id -> prompt}` for the entry's questionnaire, in corpus order."""
    return {a["id"]: a.get("prompt") or ""
            for a in (entry.questionnaire.get("anchors") or []) if a.get("id")}


def _corpus_person(entry, person_name: str):
    for person in entry.people():
        if person.person == person_name:
            return person
    raise KeyError(f"{entry.id} names no person {person_name!r}")


def plan(host_prompts: Sequence[str], entry, person_name: str,
         values_by_index: Mapping[int, Sequence[tuple[str, str]]] | None = None,
         *, floor: int = FLOOR) -> list[AnchorPlan]:
    """One `AnchorPlan` per anchor the host wrote, in the page's own order.

    Pure: the corpus entry, the prompts the page drew, and the picks already decided per anchor.
    No browser, no network, no clock -- so the whole of *which words this stranger types and why*
    is a unit test, and the live run only has to type them.
    """
    person = _corpus_person(entry, person_name)
    prompts = corpus_prompts(entry)
    matched = match_occasions(host_prompts, prompts, floor=floor)
    values_by_index = values_by_index or {}

    # Only an ANCHORED story describes an occasion that happened; a GUESSED one is the corpus
    # saying this person does not have one, and lifting a thing or a when out of it would be this
    # module committing the very sin it exists to undo.
    anchored = {aid: (written or {}) for aid, written in person.anchors.items()
                if (written or {}).get("anchoring") == "ANCHORED"
                and ((written or {}).get("text") or "").strip()}

    out: list[AnchorPlan] = []
    for index, host_prompt in enumerate(host_prompts):
        anchor_id = matched.get(index)
        scores = scores_against(host_prompt, prompts)
        written = (person.anchors.get(anchor_id) or {}) if anchor_id else {}
        text = (written.get("text") or "").strip()

        if anchor_id and text:
            out.append(AnchorPlan(
                index=index, host_prompt=host_prompt, path=THEIR_OWN_STORY, text=text,
                corpus_anchor=anchor_id, anchoring=written.get("anchoring"), scores=scores,
                why=(f"{person_name}'s own {anchor_id} story: the host's occasion and the "
                     f"corpus's share {scores.get(anchor_id, 0)} content words, more than any "
                     f"other pair")))
            continue

        if anchor_id and written.get("tap"):
            out.append(AnchorPlan(
                index=index, host_prompt=host_prompt, path=ESCAPE,
                tap=tap_enum(written["tap"]), corpus_anchor=anchor_id, scores=scores,
                why=(f"the corpus leaves {person_name}'s {anchor_id} blank and taps "
                     f"{written['tap']!r} -- an honest escape, which keel-cloud counts as one, "
                     f"and never a guess dressed as a story")))
            continue

        # Nothing of this person's matches this occasion. Compose from their own facts: the thing
        # the nearest occasion names (or, where that occasion names none, the nearest one that
        # does), the when it carries, and the picks about to be ticked on this very anchor.
        order = ([anchor_id] if anchor_id in anchored else []) + \
                [aid for aid in anchored if aid != anchor_id]
        thing = thing_from = None
        when = when_from = None
        for aid in order:
            story = anchored[aid]["text"]
            if thing is None and (found := thing_in(story)):
                thing, thing_from = found, aid
            if when is None and (found := when_in(story)):
                when, when_from = found, aid
        values = list(values_by_index.get(index) or ())
        text = compose(host_prompt, thing=thing, when=when, values=values)
        if text:
            out.append(AnchorPlan(
                index=index, host_prompt=host_prompt, path=COMPOSED, text=text,
                corpus_anchor=anchor_id, anchoring=(written.get("anchoring") if anchor_id else None),
                scores=scores, thing=thing, thing_from=thing_from, when=when, when_from=when_from,
                values_used=tuple(f"{p[:40]} -> {v}" for p, v in values),
                why=(f"no corpus occasion of {person_name}'s is about this one (best score "
                     f"{max(scores.values(), default=0)}, floor {floor}), so the sentence is "
                     f"their own thing from {thing_from}, their own when from {when_from}, and "
                     f"the {len(values)} picks this anchor is about to be given")))
            continue

        out.append(AnchorPlan(
            index=index, host_prompt=host_prompt, path=ESCAPE, tap=tap_enum("can't recall"),
            corpus_anchor=anchor_id, scores=scores,
            why=(f"{person_name} has no anchored occasion this sentence could be built from, so "
                 f"the escape is tapped rather than a sentence invented")))
    return out


def typed(plans: Iterable[AnchorPlan]) -> list[dict]:
    """The bundle's own record of what the stranger did, anchor by anchor."""
    return [p.recorded() for p in plans]
