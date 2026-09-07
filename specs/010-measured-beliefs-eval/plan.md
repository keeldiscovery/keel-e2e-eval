# Implementation Plan: The eval set, rewritten for measured beliefs

**Branch**: `010-measured-beliefs-eval` | **Date**: 2026-09-07 | **Spec**: [spec.md](./spec.md)

**Input**: [spec.md](./spec.md), and the three siblings this feature is a referee of, read at the
commits named below and **vendored** — copied into `contracts/` with their commit — rather than
assumed:

| Sibling | Branch | Commit read | What was taken from it |
|---|---|---|---|
| keel-cloud | `028-measured-beliefs-aggregate` | `03ebe60` | `ScreenContextBuilder`'s key table (via its own `screenContracts export`), the founder wire spec 030 landed, the frozen corpus, the two 029 result contracts |
| keel-web | `013-measured-beliefs-screens` | `c887aac` | the routes, and the DOM the page objects hold on to |
| keel-runtime | `timeout-configurable` | `89b1396` | the scripted executor this feature's RT section asks to be rebuilt |

**On the artefact set.** Specs 004–008 in this repo are `spec.md` + `tasks.md` and nothing else,
and that is the right shape for one scenario. This is not one scenario. It rewrites four, adds
three, moves a version constant, invents a generator with a file format, and asks for a change in
another repository. So it has the shape spec 009 had: a plan, a research note, a data model, a
contracts directory and a quickstart — and, new here, a **vendored-facts** contract, because the
whole risk of this feature is planning against three moving siblings.

## Summary

Rewrite `evals/` against the measured-beliefs model. One new harness module,
`harness/corpus_script.py`, turns a corpus entry into (a) a keel-runtime scripted-executor script
and (b) the founder's and each person's typed inputs; three new scenarios drive `01-countly`,
`05-paidly` and `07-mulchrun` through the real screens and assert each entry's own `expected`
section where a founder reads it; the smoke keeps the journey and gets a corpus-shaped fixture of
its own; every-door grows a fifth rule for openers; the stranger-who-gives-orders grows from two
boxes to nine; and `evals/policy.py` goes to version 8 with a measured-beliefs vocabulary,
retired strings, new hop ids, two new checks, and `Fact.absent_hops` finally honoured.

**Technical approach**: the same discipline spec 009 set — *nothing is copied that can be asked
for*. The corpus is read through `instructions/corpus.py` (one reader, one hash). keel-cloud's
context keys are read from its own `screenContracts export`, not retyped. keel-web's DOM is held
by page objects and nowhere else, so a screen that moves is one file's problem. keel-cloud's
`expected` numbers are the assertion, so a green run means the product agrees with the same golden
truth spec 009 measured the instructions against.

**The one thing that is genuinely new and hard**: keel-web has **no `data-testid` convention**
(one testid exists in the whole tree, `median-tick`). Every handle is a role, a label, a heading
or a stable class. That is fine — the spec already forbids naming selectors in assertions — but it
makes the page-object layer load-bearing rather than decorative, and it is why §Page objects below
is the longest section of this plan.

## Technical Context

**Language/Version**: Python 3.11+, as `harness/`, `evals/`, `stack/` and `instructions/` already
are.

**Primary Dependencies**: `pytest`, `playwright`, `requests`, `pyyaml` — all four already in
`requirements.txt`. **No new dependency.** `harness/corpus_script.py` imports
`instructions.corpus` and `instructions.context` (for the tap table) and nothing else new.

**Storage**: `runs/<id>/` and nothing else. `script.json` and `inputs.json` join
`transcript.jsonl`, `versions.json`, `scorecard.json`, `verdict.json`, `screenshots/` and
`report.html` in the bundle. Nothing generated is committed.

**Testing**: `pytest evals` (`make eval`) against a booted stack for the scenarios; `pytest tests`
(`make unit`) with no stack at all for the generator, the D5 judge and policy 8.

**Target Platform**: a developer's machine with Docker, the three sibling checkouts `stack.toml`
names, and Chromium. S-004 additionally needs a logged-in `claude`.

**Project Type**: unchanged — `stack/` boots it, `harness/` drives it, `evals/` asserts it,
`instructions/` is a library this feature reads and never writes.

**Performance Goals**: none, but a **run-length** goal, because these scenarios are long:
`05-paidly` types twenty people's answers through a browser. The generator emits every person's
picks as data and the participant page object fills a whole selection block in one pass; a run
that takes longer than S-001's does is acceptable, one that takes longer than the stack's own
fixture timeouts is not, and `runs/<id>/report.html` prints per-step durations already.

**Constraints**: the corpus is read-only and hash-checked at the end of every run (FR-005); the
repo reports and never fixes; scenarios are deterministic except S-004; `instructions/` is imported
and never written (SC-008); `MARKS_VERSION` is untouched.

**Scale/Scope**: 1 new harness module, 1 new fact-registry module, 1 new fixture YAML, 3 new
scenario modules, 4 rewritten ones, ~10 new/rewritten page objects in `harness/browser.py`, 1 new
door rule in `harness/doors.py`, `evals/policy.py` at 8, `harness/rubric.py` taught `absent_hops`,
4 new unit-test modules, 2 docs, and a `runs/DRIFT.md` that starts at #30.

## Constitution Check

*GATE: passed before Phase 0; re-checked after Phase 1.*

`.specify/memory/constitution.md` is still the unfilled spec-kit template, as specs 001 and 009
recorded. The binding rules are `AGENTS.md`'s, checked the same way:

| Inherited rule | How this feature meets it | Post-design |
|---|---|---|
| **The repo owns no product code and never fixes the product** | Three siblings are read; none is written. The RT section is a *requirement on* keel-runtime, delivered as a spec section, not a patch. keel-web's nine open wire gaps become DRIFT entries and absent-by-default page objects, never a workaround that hides them. | Pass |
| **The scenarios are deterministic; no LLM except in two named places** | The two named places do not change in number or in name. S-005–S-007 are scripted, like S-001. `make eval-all` still deselects `live`. | Pass |
| **Every journey assertion cites its `§`** | FR-009: the `§` lines stay in the scenario files; `tests/test_journey_coverage.py` is unchanged until keel-cloud's ledger gains the S-005–S-007 rows — the pattern spec 007 FR-005 set. | Pass |
| **A rubric change bumps its version** | `POLICY_VERSION` 7 → 8, in the same commit as the checks it describes. `MARKS_VERSION` untouched. | Pass |
| **The evidence bundle is the product of a run** | `script.json` and `inputs.json` are added *to the bundle*, so a reader sees corpus, screen and wire side by side (SC-009). | Pass |
| **Two referee sessions never share a profile** | Unchanged; S-004's quickstart still says `PROFILE=playground`. Seven scenarios on one profile is one session, not seven. | Pass |
| **Contract authority is the running sibling itself** | Strengthened again: keel-cloud's context keys and result schemas come from *its own exporter*, and every field this feature depends on is vendored with its commit in `contracts/vendored-wire-facts.md`. | Pass |

**Post-design re-check.** Two judgements are worth recording.

1. **A scenario asserts the design, not the build** (spec judgement call 7) survived contact with
   the real siblings and got *bigger*: keel-cloud landed every field spec 030 promised, and
   keel-web has not re-vendored its OpenAPI copy yet, so nine of its screens' features are live
   stubs (`// wire gap N`). The plan does not soften a single assertion for that. It writes one
   task per gap whose whole content is *the fact is vendored; the assertion is written; it closes
   when the screen renders it* — and, until then, red is the finding.
2. **The page-object layer is a real abstraction and is allowed to be.** `AGENTS.md` is hostile to
   abstraction for its own sake (`evals/scenario.py` was retired for exactly that). This one earns
   its keep on a measurement: with no testid convention in keel-web, the alternative is the same
   class selector written in seven scenario files, and the next keel-web pass makes seven scenarios
   red for one reason. Page objects keep that at one file. They hold selectors; they never hold
   assertions.

## Project Structure

### Documentation (this feature)

```text
specs/010-measured-beliefs-eval/
├── spec.md
├── plan.md                              # this file
├── research.md                          # Phase 0 — R1..R12
├── data-model.md                        # Phase 1 — the generated script, the typed inputs, the hop map, the facts
├── quickstart.md                        # Phase 1 — boot, generate, run one, read the bundle
├── contracts/
│   ├── generated-script-contract.md     # what harness/corpus_script.py emits, exactly
│   ├── vendored-wire-facts.md           # every sibling field this feature depends on, with its commit
│   └── policy-v8-contract.md            # hops, tokens, retired strings, the two new checks
└── tasks.md                             # Phase 2 (/speckit-tasks)
```

### Source (repository root)

```text
harness/
├── corpus_script.py     # NEW — FR-001..FR-006: entry -> script + typed inputs, and the drift-case fold
├── browser.py           # page objects: MarketStep, ReviewCard, CorrectionChat, Overview,
│                        #   OpenedCard, SaidBox, AnswersModal, PrintPage, ParticipantPage (rewritten),
│                        #   People (retargeted); Brief retired
├── doors.py             # + D5 "every opener", Verdict.opens_nothing
├── rubric.py            # + Fact.absent_hops honoured (FR-030), ORI-U4, GUI-U4
└── evidence.py          # + script.json / inputs.json into the bundle and the report

evals/
├── policy.py                 # POLICY_VERSION 8 (FR-025..FR-029)
├── facts.py                  # unchanged — absent_hops was already there, unused
├── corpus_facts.py           # NEW — FR-011/FR-030: one fact registry built from any entry
├── payroll_exceptions.yaml   # NEW — FR-007: the smoke's fixture, in the corpus's own shape
├── payroll_exceptions.py     # loader + facts() for the above; old literals gone (FR-010)
├── test_s001_smoke.py        # rewritten (FR-008)
├── test_s003_every_door.py   # retargeted (FR-017..FR-019)
├── test_s004_stranger_who_gives_orders.py  # nine boxes, eight attacks (FR-020..FR-024)
├── test_s005_countly.py      # NEW
├── test_s006_paidly.py       # NEW
└── test_s007_mulchrun.py     # NEW

tests/
├── test_corpus_script.py     # NEW — the generator, incl. FR-004's four refusals
├── test_doors_d5.py          # NEW — the opener judge against canned DOMs
├── test_policy_v8.py         # NEW — tokens, retired strings, hops, ORI-U4/GUI-U4
└── test_scoring_seeded_loss.py  # + one seeded loss per new check

README.md  AGENTS.md          # FR-034
runs/DRIFT.md                 # #30 onwards
```

**Structure Decision**: no new top-level package. Spec 009 got one because its subject was a
model; this feature's subject is the same four applications the existing four scenarios referee,
so it lives where they live. The one new `harness/` module is machinery two or more scenarios
share, which is exactly what `harness/` is for.

## The page objects

Named here because the spec deliberately refused to (`Out of scope`: "keel-web's routes and
selectors… the mapping to routes belongs to the plan"). Each is a class in `harness/browser.py`
in the existing shape — a `page`, a `_BrowserStep`, an interaction scope, `capture_text(hop, …)`
for the hops policy 8 knows, and screenshots. **No page object asserts anything.**

| Page object | Route it opens | Hop it captures | The handles it owns (keel-web `c887aac`) |
|---|---|---|---|
| `Landing` (existing) | `/` | — | `.project-row`, the name step's `h2.guided-step__question`, its input's `aria-label` |
| `MarketStep` **new** | `/` (inline step 2) | `stage_screen` | the country `<select aria-label="Where will you sell this first?">` with its three `<optgroup>`, the region `<input>` **found positionally** (its `aria-label` is the country-dependent placeholder — R7), `p.hint`'s derived sentence, `Back` / `Start` |
| `ReviewCard` **new** | `/p/:id/s/:stage` while unframed | `review_card` | `div.card.openc`, `span.bet`, `p.claim`, `div.who > h4`, `p.rule-line`, `div.belief` (`span.b-num`, `span.b-heading`, `span.stand-in` = *asked indirectly*, `p.you-said`, `div.chips > span.chip[.expected|.band|.esc]`), the `dl.qa` of *What they'll be asked first*, `ul.rationale > li`, `Redo the whole claim`, `These are right — approve` |
| `CorrectionChat` **new** | same route | `review_card` | `div.chat`, `div.chat__body > div.msg.you|.agent`, the composer `input[aria-label="Say what you meant…"]`, `Send` |
| `Overview` **new** | `/p/:id` | `overview` | `div.evidence` (`span.evidence__title`, `span.evidence__pct`, `div.bar`, `div.legend > span.up/.down/.split/.none`), `div.next > b` = *What this says*, `div.ocards` cards (`span.bet`, `span.status`, `p.claim`, `span.counts`, `span.must`, `span.see`), the `Download as PDF` **link** |
| `OpenedCard` **new** | `/p/:id/s/:stage` while framed | `opened_card` | `div.key`, `div.measures.lines > h4`, each `div.strip` (`span.caret`, `span.b-num`, `<b>`, `span.db`, `span.strip__you`, `span.strip__status`, `span.strip__read`), and the SVG: `circle[role=button][aria-label=<person>]`, `rect[role=button][aria-label=<person>]`, `line[data-testid="median-tick"]` |
| `SaidBox` **new** | in-page | `opened_card` | `div.said` (`span.n`, `span.k`, `span.w`, `span.r`), `button.x[aria-label="Close"]`, `See all of <First>'s answers` |
| `AnswersModal` **new** | in-page | `answers_modal` | `div.pop[role=dialog]`, `h2`, `p.story`, `div.p-sec`, `p.p-q`, the four ways to close (scrim, `button.x`, footer `Close`, `Escape`) |
| `PrintPage` **new** | `/p/:id/print` | `download` | `div.pages > div.page`, `div.ptitle`, `h2` *Overview*, `table.ptab` with its four `<th>`, `div.pquotes`; and the stylesheet's own page-break rule, read off the computed style, never off a pixel |
| `ParticipantPage` **rewritten** | `/i/:token` | `participant_page` | `p.hello` introduction, per-anchor `div.q` (`textarea.box[aria-label=<prompt>]`, `div.taps > span[role=button].chip`), `div.picks` → `div.opts[role=radiogroup\|group]` → `div.opt[role=radio\|checkbox]`, the reveal `div.opt__more > input`, `Submit` |
| `People` **retargeted** | `/p/:id/people` | `invite_screen` | unchanged in shape; the answers popup's read-back keeps feeding `participant_page` |
| `Brief` **retired** | — | — | the `brief` hop retires with it (FR-026); `BriefRoute.tsx` no longer exists in keel-web |

`window.print()` fires on mount on `/p/:id/print`. `PrintPage.open()` stubs it via
`page.add_init_script` before navigation, exactly as keel-web's own e2e suite does — otherwise
every S-003 walk hangs on a native dialog. That is a harness mechanic, not an assertion, and it
is recorded in research R9.

## The corpus → script generator

`harness/corpus_script.py`, one module, four public names:

- `generate(entry) -> GeneratedScript` — the runtime script, keyed by screen.
- `founder_inputs(entry) -> FounderInputs` — name, market, three statements, one correction.
- `person_inputs(entry) -> list[PersonInputs]` — per person: role, story text per written anchor,
  tap, and one pick per selection their role is asked.
- `drift_equal(corpus_drift, wire_drift) -> bool` — the one place the corpus's lowercase `none`
  and the wire's `NONE` are reconciled (spec edge case; never a convention a scenario remembers).

It refuses rather than invents, naming entry and field, on each of FR-004's four: a belief whose
`selection` is on no anchor of its own stage; a pick naming no option and no escape; a tap outside
`instructions/context.py`'s `TAP_ENUM`; an anchoring the corpus does not carry.

Two facts the generator has to know that the spec's prose does not spell out, both vendored:

- The wire's assumptions schema has **no `askedOf`**. A belief's `askedOf` becomes
  `role: {reuse: <label>}`, or `role: {new: {label, roleType, about}}` for the first belief that
  names a role in that stage. (`contracts/vendored-wire-facts.md` §V4.)
- `assumptions` and `questionnaire.anchors` are each capped at **`maxItems: 8`** per screen. No
  chosen entry's stage exceeds it (countly's PROBLEM is 8 beliefs and 1 anchor — exactly at the
  cap, which is a fact worth a test, not a coincidence to discover in a run).

**The generated script is not committed** (spec judgement call 1). It is written to
`runs/<id>/script.json`, handed to the runtime as `KEEL_SCRIPT` through `harness/connect.py`'s
existing `env_extra`, and shown in `report.html`.

## Policy v8

`contracts/policy-v8-contract.md` is the exact list. In summary: `POLICY_VERSION` 7 → 8;
`HOP_IDS` becomes the eight FR-026 names and `brief` retires; `HOP_INTERACTION_TYPES` gains the
new hops with `participant_page` still reachable from either party; `CLARITY_TOKENS` gains the
placements, anchorings, taps, measure kinds, expectation types, marks, selection controls and role
types; `RETIRED_STRINGS` gains the three evidence-drill-down phrases; `ORI-U4` and `GUI-U4` join
`CHECKS`; and `harness/rubric.py` learns `absent_hops` — a fact declared absent that is *found* at
a hop fails FIDELITY at that hop's own weight.

Two exemptions are predicted and must be added **by name** if the sweep flags the product's own
correct copy, never by softening it: `RATE` (an ordinary English word that keel-web could
legitimately print) and `SHARE` (likewise, and the label of a control on some screens). Neither is
exempted pre-emptively — the first red run decides, and the decision is recorded in
`_ENGLISH_COLLISION_EXEMPTIONS` beside the five already there.

## The facts registry for the three entries

`evals/corpus_facts.py`, one function, `facts_for(entry) -> dict[str, Fact]`, so FR-015 holds —
the entry id is the only thing that differs between the three scenario modules:

| Fact kind | Text | `hops` | `absent_hops` |
|---|---|---|---|
| `statement` | the entry's title (project name) | `stage_screen` | — |
| `statement` | each stage's statement | `review_card`, `download` | — |
| `assumption` | each belief's `founderPhrase` | `review_card`, `opened_card` | **`participant_page`** |
| `assumption` | each `INTERVAL`'s band values, rendered as the founder's chip reads them | `review_card` | **`participant_page`** |
| `assumption` | each `CHOICE`'s `expectation.expected` option | `review_card` | **`participant_page`** |
| `role` | each role's `label` | `invite_screen` | — |
| `about_line` | each anchor's `prompt` | `participant_page`, `opened_card` | — |
| `answer` | each person's story text per written anchor | `participant_page`, `answers_modal` | — |

The `absent_hops` column is design rule `Q5` and the mockup's *"the people you ask never see
them"*, scored for the first time (FR-030).

## The live adversarial scenario's boxes

Nine, named, with where each lives — because the spec says *"every free-text box the new screens
have"* and the count only balances once it is written down (research R11 records that keel-web
spec 013's own screens carry six; the three claim boxes are the walk's chat composer, which 013
leaves untouched and which the founder still types the problem, solution and commercial claims
into):

| Box | Where | Attacks it takes (FR-021) |
|---|---|---|
| **B1** project name | landing name step, `input[aria-label="What should we call this project?"]` | A1, A3 |
| **B2** region | market step, the positional region `input` | A1, A4 |
| **B3** problem claim | the walk's chat composer at `PROBLEM_FRAME` | A1, A2 |
| **B4** solution claim | same composer at `SOLUTION_FRAME` | A2, A5 |
| **B5** commercial claim | same composer at `COMMERCIAL_FRAME` | A4, **the multi-line paste** |
| **B6** correction chat | `input[aria-label="Say what you meant…"]` on a review card | A1, **A8** (names another stage's line) |
| **B7** participant story box | `textarea.box` on the participant page | A3, **A6** (asks for the founder's numbers) |
| **B8** *say roughly* | the reveal `input` on an interval option | **A7** (tries to write the verdict) |
| **B9** *other, say what* | the reveal `input` on a multi-select | A5, A6 |

A7 lands in **B8** rather than B7 so FR-023 holds without a control run: the box belongs to a
person whose corpus anchoring for that anchor is already `GUESSED`, so `expected.standings` must
come out unchanged and exactly equal. The scenario writes the person and the anchor it chose into
the bundle.

## Phase sequencing

1. **keel-runtime first** (RT-001–RT-006, another repo, another branch). Nothing here runs until
   the executor answers the current table: today every key set misses on `market` alone.
2. **The generator, with no stack** — `harness/corpus_script.py` and `tests/test_corpus_script.py`,
   including the fixed point: `01-countly` in, and every belief, anchor, selection and answer in
   the script traceable to the entry (FR-007's acceptance scenario 7 is a unit test before it is a
   run).
3. **Policy 8 and the rubric**, still with no stack: the tokens, the retired strings, the two
   checks, `absent_hops`, and one seeded loss each.
4. **The page objects**, against a booted stack, screen by screen, with S-001 as the driver — this
   is where keel-web's nine wire gaps turn into DRIFT entries #30 onward.
5. **S-005**, the mockup entry, first of the three: every number on the overview is Countly's.
6. **S-006 and S-007**, which need only their entry id if step 2 was done right (FR-015 is the
   test of that, not a hope).
7. **S-003's D5**, then **S-004's nine boxes** — last, because S-004 attacks a project S-005 built
   and costs real money on the founder's own account.
8. **Docs and DRIFT**, and `tests/test_journey_coverage.py` when keel-cloud's ledger gains the rows.

## Complexity Tracking

| Violation | Why needed | Simpler alternative rejected because |
|---|---|---|
| **A page-object layer** (~10 classes in `harness/browser.py`) | keel-web has one `data-testid` in the whole tree; every other handle is a role, a label or a class, and spec 013's own decision D-12 says the popover and modal are deliberately not pixel-pinned. Concentrating those handles is the only way one keel-web pass does not redden seven scenarios. | Selectors inline in the scenarios is what specs 001–008 did with four screens and it was already the thing most often broken; with a popover, a modal, an SVG strip and a print page it stops being maintainable. Page objects hold selectors and never assertions, so the "no abstraction for its own sake" rule still bites. |
| **A second fact registry module** (`evals/corpus_facts.py` beside `evals/payroll_exceptions.py`) | The smoke's facts are hand-written for one journey; the corpus scenarios' are *derived from an entry*, and deriving them in each of three modules is FR-015's own failure mode. | Extending `payroll_exceptions.py` was rejected: it is the smoke's fixture, and a module that is both a fixture and a generic derivation is neither. |
| **Asserting an unbuilt field** (stage drift; and now nine keel-web wire gaps) | Spec judgement call 7, and the repo's own precedent from spec 006. A referee that only asserts what already works is a follower. | Waiting for green means the first honest run happens after the product shipped, which is when a finding is worth least. |
| **`KEEL_SCRIPT` through the environment** | The runtime may only ever be started through keel-connect-skill's own script (AGENTS.md), and that script passes its environment through. | A `--script` passthrough in keel-connect-skill touches a second application under referee and changes its stable output contract. Named in spec judgement call 2 so the founder can prefer it. |
