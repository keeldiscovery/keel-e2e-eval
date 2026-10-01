# Plan: a real story for every anchor the host wrote

**Spec**: [spec.md](spec.md) | **Tasks**: [tasks.md](tasks.md) | **Branch**: `028-journey-stories-for-every-anchor`

Five phases, each with its own tests, each a commit, `make unit` green at every one. Nothing spends a
model call, nothing opens a browser against staging, and no live journey is run from this branch.

## The shape of the change

| layer | what moves |
|---|---|
| `harness/stranger_stories.py` | **new.** The matcher, the composer, the escape and the per-anchor record — pure functions, corpus in, sentences out, no browser and no clock |
| `evals/test_s012_journey_through_a_host.py` | `_answer_whatever_is_asked` decides the picks first and writes the story from them; `_story_texts` retires into the new module; `THE_STRANGER_SAYS` becomes an asserted-never-used constant; the §1.7 panel fault becomes an accounting; one new step between §1.6 and the deck |
| `harness/corpus_script.py` | **nothing.** `PersonInputs` and `written()` are read, not changed: this repository has one reading of *wrote something* and gains no second one |
| `harness/browser.py` | **nothing.** `tell_story(prompt, text, tap)` already takes a tap, which is the only reader the escape path needs |
| `tests/test_stranger_stories.py` | **new.** The matcher and the composer against `03-lullaby` itself and against the run's own four prompts |
| `tests/test_journey_untested_stage.py` | **new.** The two assertion helpers as pure functions, including the red run's own numbers |

## Decisions

**Decision 1 — a new module, not more privates in the scenario.** The matcher and the composer are
the first thing in this repository that *writes English*, and English needs a unit test per rule.
`evals/test_s012_journey_through_a_host.py` is 2,656 lines of one scenario and the privates in it are
tested, where they are tested at all, by reading its source. A module in `harness/` is importable,
has no pytest collection semantics, and lets every rule below be a two-line test against the real
corpus entry.

**Decision 2 — the matcher scores a count, not a ratio.** A ratio rewards a short prompt for being
short, and the host's prompts are long by instruction: keel-cloud's `questions.md` puts the
qualifiers in the anchor's prompt and caps the *occasion* at eight words, not the prompt. What
matters is how much of the occasion two prompts name in common, which is a count. The stopword list
drops the four words the keel-cloud frame writes into every prompt (*think*, *tell*, *us*,
*sentence*) for the same reason a constant cannot be a signal.

**Decision 3 — the picks are decided before the story is typed, and that reorders the loop.** The
old loop typed the story, then read the options, then ticked. The new one reads the options and
decides every tick for that anchor first, then composes, then types the story, then ticks. It is the
same number of page reads in the same order of magnitude, and it is the only order in which a
composed sentence can be made to agree with the answers underneath it (FR-010). The decision is
`_their_pick`'s, unchanged.

**Decision 4 — only an ANCHORED story lends a fact.** `instructions/corpus.py` keeps `anchoring` per
person per anchor and the harness has never read it. It is read now and it is read strictly: a
`GUESSED` story is the corpus stating that this person does not have that occasion, so Keiko's *"We've
bought loads of things, I couldn't tell you which was last"* lends nothing to any other anchor, and
the anchors it cannot fill tap *I can't recall*. Lifting a thing out of a guess is the error this
branch exists to undo, committed one level down.

**Decision 5 — the thing is the story's first fragment, and the rule is the corpus's own register.**
Every purchase story in every entry opens with what was bought (*"Huckleberry, the sleep app, two
months ago. I bought it."*, *"A white-noise machine, my wife ordered it in the spring."*, *"Baby
Tracker, last month, I subscribed."*); every occasion story opens with when it happened (*"Last
night."*, *"Night before last."*, *"Wednesday."*). So the first fragment is the thing exactly when it
is **not** a time phrase, and the second joins it when it is an apposition naming the same thing.
That is a rule read off all seven entries, not a parser, and it fails closed: no thing means no
sentence means the escape.

**Decision 6 — the time phrases are read off the corpus, not imagined.** `WHEN_PATTERNS` covers what
the seven entries' `answers:` blocks actually say, listed in the module beside the patterns. A story
with none of them lends no *when*, which `plan()` records as `None` rather than papering over with a
phrase nobody wrote.

**Decision 7 — `THE_STRANGER_SAYS` stays, and a test proves it is dead.** AGENTS.md's rule is invert
or move, never delete. The constant stays where it is with its reason rewritten and
`tests/test_stranger_stories.py` asserts that the journey module names it **exactly once** — its own
definition — so the day somebody reaches for it again, a unit test says why not.

**Decision 8 — the panel assertion becomes an accounting, and the tail counts at its own number.**
`held + failed + tail(held) + tail(failed)` against `holdingUp + notHoldingUp + peopleDisagree`.
Counting only the visible rows would fail every closed panel with more than three lines in a part
(keel-web FR-015's rest-of-three), and opening the tails first would break the *worst panel open at
rest* assertion three steps later, which reads exactly those tails. So the tail's own *N* is parsed
and added, which is what *a budget moves a number, it never deletes one* means when a referee counts.

**Decision 9 — the new assertion stands before the deck, and it names the party from the wire.** It
is about the *readings*, not about any screen, so it stands where the readings finish: after §1.6's
toast, before `Overview.open`. `GET /stages/{stage}` carries `BeliefStanding.guessed` and
`inside`/`outside` per belief, which is the only place the wire says whether the answers were read as
occasions or as opinions. **Anchored zero and guessed above zero is the stranger's fault**; anything
else is the product's. Both halves are fields the wire sent — nothing is inferred, which is AGENTS.md's
house rule and the reason this assertion can be trusted to blame the right repository.

**Decision 10 — nothing in keel-cloud or keel-web is asked to change.** Run 36895521843 is a green
product and a lying referee. Writing a keel-cloud follow-up for it would be this repository
exporting its own bug.

## Risks

| risk | why it is acceptable |
|---|---|
| a composed sentence reads as a guess to INTERPRET anyway | it carries a named thing and, for Lullaby's four anchors, a when — the two things `anchoring` is decided on. The new assertion (FR-020/FR-021) is what detects it if it happens, and it names the stranger, so the next run says so in one line instead of failing a panel |
| the matcher mis-matches on an entry nobody has run live | the floor fails closed to a composed sentence, and the bundle carries every score. Unit tests cover all seven entries' anchor prompts against each other |
| the picks-first reorder changes the page's interaction order | the page is a form with no reveal between a story and its picks (`ParticipantRoute.tsx` gates picks on a *tap*, never on the story box), and `tests/test_participant_anchor_selections.py` already holds that shape offline |
