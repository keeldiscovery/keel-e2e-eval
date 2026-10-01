# Feature Specification: a real story for every anchor the host wrote — the stranger stops guessing, and §1.7 stops calling an all-untested stage a panel fault

**Feature Branch**: `028-journey-stories-for-every-anchor`

**Created**: 2026-10-01

**Status**: **Draft for implementation.** Nothing here spends anything. The one paid thing this spec
produces is a *command* — the founder's next live S-012 run — written down in *The next live run* of
[tasks.md](tasks.md) rather than typed by this pass.

**Input**: the run, the corpus and the code of record, read in full —

- **the red run**: the live Lullaby journey, matrix run **36895521843**, against staging keel-cloud
  **f6aa07d** (keel-cloud specs 048 + 049 + 050 + 051) and keel-web **cdfa60f**. Bundle
  `20261001T165730Z-s012-journey-claude`. The trigger fix (keel-cloud 051) **held**: the journey got
  through all three stages, the project's one questionnaire, five invitations, five answers and five
  readings, and reached the deck. Transcript seqs read in full: **68–70** (the one questionnaire — 4
  anchors `A1`…`A4`, 15 selections, sections *about the last night the baby cried / checking an app
  during a night waking / the last baby app you bought / a baby app you pay for now*), **88–110** and
  **155–176** (two participants' answers), **247** (the reading toast: *"Seven things moved on the
  problem card and four on your solution"* — and nothing at all on the commercial), **251** (the
  failure: `COMMERCIAL: 5 lines on the wire and the panel shows none of them`, the wire's own numbers
  `holdingUp 0, notHoldingUp 0, peopleDisagree 0, untested 5`, `peopleAnswered 5`).
- keel-cloud `canon/designs/measured-beliefs/corpus/03-lullaby.yaml` at this checkout — the
  **revised** entry (2026-09-30, `one-occasion-once-design.md` §8.2): `A1` and `A2` merged into one
  occasion, so the entry carries **two** anchors, `A1` (PROBLEM + SOLUTION) and `A3` (COMMERCIAL),
  and **two stories per person**. Every person's `answers:` block, their `anchoring`, their taps and
  their twelve picks.
- keel-cloud `canon/openapi-v2.yaml` — `BeliefStanding` (`verdict`, `inside`, `outside`, `guessed`,
  `escaped`, `optionCounts`), its own words for `guessed`: ***"answers shown to the founder that
  count towards nothing"***; `StageCard.groups[].loadBearing/supporting`; `Standing` (`holdingUp`,
  `notHoldingUp`, `peopleDisagree`, `untested`), `StageSummary.peopleAnswered`, `StandingLines`.
- this repository at `master` `581dc0b`: `harness/corpus_script.py` (`PersonInputs`, `AnchorAnswer`,
  `written()`, `person_inputs`, `people_to_invite`), `evals/test_s012_journey_through_a_host.py`
  (`THE_STRANGER_SAYS` at line 935, `_story_texts` at 946, `_their_pick` at 957,
  `_answer_whatever_is_asked` at 1026 with its order assumption at 1049–1090, `_stage_lines` at 627,
  the §1.7 panel assertion at 2146–2203), `harness/browser.py` (`ParticipantPage.tell_story`,
  `options_for`, `pick`; `Overview.panels`, `part_of`, `lines_of`, `tail_of`),
  `instructions/corpus.py` (`Entry`, `Person.written`), `instructions/context.py` (`tap_enum`).
- `AGENTS.md` — this repository's governing document. `.specify/memory/constitution.md` is still an
  unfilled template, as spec 027 recorded; there is nothing to check a spec against there.

## The one sentence

**The stranger stops lying about having an occasion: every anchor the host wrote gets either this
corpus person's own matching story, or a first-person sentence composed from that person's own facts
and the very picks the harness is about to tick, or an honest tap — and §1.7 stops reading an
all-untested stage as a panel fault, while a new assertion before the deck catches the thing that
actually went wrong.**

## Why this exists

Run 36895521843 failed for a reason that is not a bug in the product. The host model wrote **four**
anchors. Lullaby's revised corpus gives each person **two** stories. `_answer_whatever_is_asked`
walked the host's anchors in page order, handed out the corpus person's stories by **position**, and
typed a filler under every anchor past the end:

> `THE_STRANGER_SAYS = "I am thinking of the last time this happened to me, and it went much the way I described above."`

keel-cloud's INTERPRET reads that sentence correctly. It is not an occasion. It is a person saying
they are thinking of one. So the answer was marked a **guess**, and a guess is `BeliefStanding`'s own
*"answers shown to the founder that count towards nothing"*. The five commercial picks — *I did*,
*nobody*, *yes*, *under £0.50*, *a monthly subscription* — were made, stored, shown, and counted for
nothing. `untested: 5` of `total: 5`, with `peopleAnswered: 5`. The reading toast said it in the
founder's own words and nobody heard it: *"Seven things moved on the problem card and four on your
solution"* — **nothing on the commercial**.

Two things are therefore wrong in this repository, and neither is in keel-cloud:

1. **The stranger.** A referee that types a guess and then fails the product for not counting it is
   not refereeing. And the order assumption made it worse than the shortfall: the corpus's
   app-purchase story landed under the host's *"opened an app during a night waking"* because that
   anchor came second on the page, leaving the host's *"the last baby app you bought"* — the one
   occasion that story **is** about — holding the filler.
2. **The §1.7 assertion.** `if counted["total"] and not (held or failed)` reads *this stage has lines
   and the panel shows none of them* as a fault. For an all-untested stage that is **correct
   behaviour**: a panel has two parts, *Held* and *Did not hold*, and no third one, so a stage whose
   every line is untested draws no rows and must. The assertion fired on the product for doing
   exactly what keel-web spec 027 says. It named the wrong party, which is the worst thing a referee
   can do, and it masked the real finding — which nothing asserted at all.

## Requirements

### The matcher — an occasion is matched by what it is about

- **FR-001** The harness MUST map the anchors the host wrote onto the corpus person's occasions by
  **prompt content**, not by position. Two prompts' closeness is the number of content words they
  share, where content words drop function words and the four the keel-cloud frame puts in every
  prompt it writes (*think*, *tell*, *us*, *sentence*).
- **FR-002** The mapping MUST be **globally best first**: the highest-scoring pair anywhere in the
  grid is taken, both sides retired, and the step repeated. A per-anchor greedy pass in page order is
  precisely what produced the red run's misplacement, and MUST NOT be used.
- **FR-003** Each corpus occasion MUST be spent at most once and each host anchor filled at most
  once. One occasion is asked once (`one-occasion-once-design.md` §8.2); typing one story twice would
  be the same lie in a new place.
- **FR-004** A pair scoring below a floor of **two** shared content words MUST NOT be matched. Being
  wrong below the floor costs a composed sentence in place of a story, which is the safe direction;
  being wrong above it types a story under an occasion it is not about.
- **FR-005** Ties MUST break deterministically — corpus order, then host order — so the mapping is a
  pure function of its inputs and the bundle is enough to reproduce it.
- **FR-006** The matcher's full arithmetic — every host anchor's score against every corpus occasion
  — MUST be recorded in the bundle, so a reader who disagrees with a match can see what it beat.

### The composer — a sentence from this person's own facts, agreeing with their own picks

- **FR-007** For a host anchor no corpus occasion matches, the harness MUST compose **one anchored
  first-person sentence** naming a concrete thing and, where the person's own words carry one, a
  when. The filler MUST NOT be typed.
- **FR-008** Every noun in a composed sentence MUST come from the corpus person's own story text or
  from a value the page itself offered. The module supplies grammar — a lead verb, a comma, an
  article's case — and nothing else. No price, no date, no product and no person is invented.
- **FR-009** Only an **ANCHORED** corpus story may supply the thing or the when. A `GUESSED` story is
  the corpus saying this person has no such occasion, and lifting a fact out of it would commit the
  very error this spec removes.
- **FR-010** The picks MUST be decided **before** the sentence is written, and the sentence composed
  from them: `(selection prompt, value)` pairs for that anchor's own selections, in the page's order.
  A story that contradicts the answers beneath it is a worse witness than one that guesses.
- **FR-011** A bare *yes* / *no* / escape value MUST be dropped from a composed sentence — it anchors
  nothing — and still ticked on the page.
- **FR-012** A money bucket MUST keep its own edges (*under £0.50*, *£5 to £10*) and gain *a month*
  only where the selection it answers asked per month. Rounding a bucket to a number would invent a
  figure the person never gave, which is the corpus's own rule for `Pick.roughly`.
- **FR-013** The lead verb MUST be chosen from a word in **the host's own prompt** (*bought* /
  *opened* / a present-tense *pay for* / the fallback *It was*), and the value-to-clause table keyed
  on the **shape of a value**, never on a corpus entry's name. An unknown value is used verbatim.

### The escape — honest, and only where the corpus says so

- **FR-014** Where the matched occasion is blank for this person and the corpus taps it (`tap:
  hasn't happened`), the harness MUST tap that tap. keel-cloud counts an escape as an answer; it does
  not count a guess.
- **FR-015** Where no corpus occasion matches **and** the person has no anchored story any sentence
  could be built from, the harness MUST tap *I can't recall* rather than invent one.
- **FR-016** Which of the three paths each anchor took, and where every part of a composed sentence
  came from, MUST be recorded in the bundle under §2.3.
- **FR-017** `THE_STRANGER_SAYS` MUST remain in the journey module as a named constant that is
  **asserted never to be used**, with its own reason above it. A deleted constant is a lesson nobody
  can grep for.

### §1.7 — the panel accounts for the tested lines, and an all-untested stage is a correct zero

- **FR-018** A panel's *Held* + *Did not hold* rows MUST equal the wire's **tested** lines for that
  stage — `holdingUp + notHoldingUp + peopleDisagree` from `GET /standing` — with each part's tail
  (*N more ›*) counted at its own number, because a budget moves a number and never deletes one
  (keel-web FR-015).
- **FR-019** A stage whose every line is `untested` MUST therefore be a **correct zero** and not a
  fault. The replaced assertion (`counted["total"] and not (held or failed)`) MUST NOT survive in any
  form: it is the one that named the wrong party.

### The new assertion — the fault the red run actually showed

- **FR-020** After the readings and **before** the deck's own assertions, the journey MUST assert
  that no approved stage is entirely untested when every participant answered: a fault is
  `untested == total` on a stage whose `peopleAnswered` is at least the number of people invited.
- **FR-021** That assertion MUST name the party by reading the wire: for each stage, the sum over its
  beliefs of `standing.guessed` and of `standing.inside + standing.outside` (the anchored answers
  that count), from `GET /v2/projects/{id}/stages/{stage}`. **Anchored zero with guessed above zero is
  the stranger's fault** — the harness typed something that is not an occasion. Anything else is the
  product's, and the message says which.
- **FR-022** It MUST assert, never infer: every number in it is a field the wire sent. The referee
  computes no verdict, no median and no standing (AGENTS.md's house rule).

## Out of scope

- **`_their_pick`'s exact-value match.** The red run shows nine of Amira's fifteen picks taken as
  *the page's own first option* because the host's label differs from the corpus's by wording
  (*monthly subscription* against *a monthly subscription*). That is a real finding, it is recorded in
  [tasks.md](tasks.md)'s **Discovered** as **D-05**, and loosening the match is a separate change with
  its own risk of ticking an option the person never gave. The composer reads whatever `_their_pick`
  decided, so the story and the pick agree either way.
- **keel-cloud and keel-web.** Nothing in either repository is at fault in run 36895521843 and
  nothing here asks for a change in either.
- **The corpus.** Lullaby carries two occasions per person on purpose. A referee that needed the
  corpus widened every time a model wrote one more anchor would be a referee that cannot read a live
  project.

## Success criteria

- **SC-001** On Lullaby's four live anchors, the matcher gives `A1` → the night-waking occasion and
  `A3` → the purchase occasion, whatever order the host wrote them in, and composes for the other
  two. Held as a unit test against the corpus itself, not a fixture.
- **SC-002** Every one of the five invited people types four anchored answers and no filler.
- **SC-003** `make unit` green at every commit, no test deleted, no assertion removed.
- **SC-004** An all-untested stage passes the panel assertion and fails the new one, with the
  message naming the stranger or the product from the wire's own `guessed`/anchored counts.
