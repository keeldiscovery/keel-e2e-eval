# Plan: the live journey reads the deck

**Spec**: [spec.md](spec.md) | **Tasks**: [tasks.md](tasks.md) | **Branch**: `027-journey-brief-ship`

Six phases, each with its own tests, each a commit, `make unit` green at every one. Nothing spends a
model call and nothing opens a browser against staging.

## The shape of the change

| layer | what moves |
|---|---|
| `harness/browser.py` | `Overview` becomes the deck's page object and keeps every retired reader; `PrintPage` becomes the five-page sheet's and gains page 1 and page 5 |
| `evals/test_s012_journey_through_a_host.py` | §1.7 becomes the deck plus the brief; a new pre-invite step reads the download's disabled state |
| `evals/test_s001_smoke.py`, `evals/corpus_scenario.py`, `evals/test_s005_countly.py`, `evals/test_s007_mulchrun.py`, `evals/tools/curated_proof_run.py` | the same four moves, in the scenarios that also read this screen |
| `harness/rubric.py`, `evals/policy.py` | **nothing.** Two *readers* move, in `browser.py`; no check's meaning does |
| `tests/test_journey_brief_ship_markup.py` | new: keel-web's own markup through both page objects, in a real browser, offline |

## Decisions

**Decision 1 — the retired readers are kept and answer empty, not deleted.** `evidence_line`,
`legend`, `stage_cards`, `what_this_says` and the rest stay on `Overview`, each answering empty on
the deck and each documenting the read that succeeded it. Three reasons. *The old screen is gone* is
itself an assertion a scenario makes, and it needs a reader to make it with. Deleting them would
break `tests/test_page_object_calls_exist.py` for every scenario at once, turning a scoped change
into a repository-wide one. And AGENTS.md's rule — invert or move, never delete — reads naturally
onto a reader as well as onto an assertion.

**Decision 2 — the wait selector is a class constant, and it lists four things.** `Overview.DECK` is
`".deck, .ship, .panels, .guided-step"`. `.deck` alone would break the moment keel-web's phone shell
wraps it; `.ship` alone would break if a frame ever drew the panels without the figure; and
`.guided-step` has to be in it because the journey opens this page object long before the deck can
render. Four alternatives is not a loosened wait: each one is a distinct, nameable rendering of this
one route, and `is_deck()` is how a caller tells the deck from the walk.

**Decision 3 — one `evaluate` per panel, not a tree of locators.** `dl.panel__body` is a flat run of
`dt`/`dd` pairs, so pairing a part's label with its own rows is a walk over sibling nodes and not
something a CSS selector can express. One JS function per panel returns the whole structure, reads
`textContent` rather than `innerText` (so the CSS-uppercased `dt` comes back as *Held*, not *HELD*,
and a deploy's `text-transform` is never the thing under test), and touches nothing the page did not
already draw.

**Decision 4 — the verdict→wash mapping is restated in Python, and that is not recomputing.** `GET
/overview` sends `verdict`; keel-web paints `band--good`/`warn`/`bad`/`none` from it through
`measuredStatus`+`washOf`. To say *this band is coloured for the verdict the wire sent* the referee
must know that mapping, so `_WASH_OF_VERDICT` and `_WORST_FIRST` are written out in
`evals/test_s012_journey_through_a_host.py` beside a comment saying where they were read from. Every
input is a field the wire sent; nothing here decides a verdict, a median or a standing. The same
rule is why *N of M lines holding* is checked by filtering `GET /standing`'s own four lists rather
than by counting rows on the screen.

**Decision 5 — *open at rest* is read as *no tail*.** keel-web FR-016 says the worst panel is
expanded. There is no `aria-expanded`, no `open` attribute and no class for it: the open state is
component state, and what it produces in the DOM is the absence of a `button.more`. So the assertion
is *this panel carries no tail*, which is exactly what *open* means here and is stable against the
rest-of-three limit moving. The `panel--worst` marker is asserted beside it, because that marker is
what keel-web's phone CSS hoists.

**Decision 6 — the journey reaches the sheet by URL, not by the founder's click.** The download is
`target="_blank"`, so clicking it opens a second tab. The journey asserts the link — its label, its
enabled state and its `href` — on the deck, and then `PrintPage.open(project_id)` navigates the one
page it already has. One context, one tab, no popup to manage in the middle of a live run.
`Overview.download()` is kept and fixed for the callers that do want the click (S-001's §1.10), and
it answers whichever `Page` the sheet landed on.

**Decision 7 — `stub_print` installs on the context where there is one.** `window.print` is
replaced with a no-op before navigation, because `PrintRoute` raises the dialog as soon as its five
reads land and no Playwright locator can dismiss a native one. A page-scoped `add_init_script` is
not inherited by a tab the founder's own click opens, so the stub goes on the context, falling back
to the page for a `set_content` page in a markup test.

**Decision 8 — the paragraph reader is scoped to page 1, and the scope is the assertion.** Pages 2–4
each draw a `p.pclaim`. A sheet-wide read would compare the problem stage's claim against
`Overview.whatThisSays` and fail on a correct product — or, worse, pass on the wrong sentence if the
two ever happened to agree. `PrintPage.what_this_says_paragraph()` reads page 1's own `p.pclaim`,
and a markup case draws a sheet with no paragraph and three claims to prove the scope holds.

**Decision 9 — `table_columns()` is re-scoped rather than renamed.** Its callers assert the three
named columns of each stage table. Page 5's table is a `table.ptab` too, so the sheet-wide read
returns a fourth row whose columns are the evidence page's. Re-scoping to the stage pages keeps
every caller's assertion exactly as it was; `evidence_page()` is the new reader for the new page,
and `table_rows(index)` stays indexed over the sheet's own tables so that `3` is the evidence one.

**Decision 10 — GUI-U1's reader moves and the check does not.** `harness/rubric.py` asks *where a
stage still needs something, does this screen offer a way onward* and reads the `affordance` capture.
The deck's ways onward are each panel's stage link, each band's link and the download, so
`Overview.AFFORDANCE` names them — and keeps `.ocards .see` and `.evidence__people a` at the end of
the list, so an older bundle and an older deploy read the same. `evals/policy.py` is byte-identical.
The `what_this_says` capture key moves the same way: it leaves `Overview._capture` and appears,
under the same name, in `PrintPage._capture`, so a bundle's reader finds the paragraph where they
have always found it, on the one screen that draws it.

**Decision 11 — the markup tests are the gate, and they are written first within each phase.** A
page object cannot be proved against a deployed screen without a live run, and a live run costs real
money and twenty minutes. keel-web's markup, condensed to the nodes the page object reads, in a real
Chromium, offline, is the closest honest thing — and it is what `tests/test_review_card_chips_markup.py`
established for exactly this failure one spec ago.

## Phases

1. **Read before writing anything.** The two designs, keel-web's spec and Discovered, keel-web's own
   markup at `7e5a2a8`, this repository's blast radius, and the red run.
2. **The page objects, with their markup tests in the same commit.** `Overview` becomes the deck's;
   `PrintPage` becomes the sheet's; `tests/test_journey_brief_ship_markup.py` proves both.
3. **§1.7 of the live journey.** The pre-invite disabled-download step, the deck's four steps, the
   brief's two.
4. **The sweep.** S-001, `corpus_scenario`, S-005, S-007, and the curated-proof tool.
5. **The ledger and the governing documents.** `tasks.md`'s Discovered, `AGENTS.md`/`README.md` where
   a sentence in them stopped being true.
6. **The command.** The dispatch inputs for the founder's next live run, written down and not typed.
