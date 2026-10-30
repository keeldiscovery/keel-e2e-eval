# Spec 097 -- The harness's context walker turns two pages: the four fields, then the recall window's own page

keel-web 141 (the founder, 2026-10-30: *"How recent should an episode be to count? is very easy to miss unless you scroll
down"*) splits step 1 into two screens: **1 of 2** the four fields with *Continue* (nothing sent), **2 of 2** the recall
window alone at `define/context/window` with *Save and continue* (today's `PUT /context`); money alone keeps the one
screen. The harness fills five controls on one form today (`harness/vectors_screens.py` `context()` `:1243-1296`,
`_save_context` `:1296`, `context_confirmed` `:1387` reads the count and unit off the form) and the quality readers'
founder-screen anchors name the context form.

## Rules

- **FR-1 The walker turns the page.** `context()` types the four fields, presses *Continue* (`context-continue`),
  waits for the window page (`context-window-page`, URL `/define/context/window`), picks the window as today (a chip
  where one matches, else count + unit), captures the page's text and a screenshot (`context-window`), and presses
  *Save and continue*; on money alone (`window is None`) it presses the form's *Save and continue* as today and
  records that no window page was drawn (`window_drawn` keeps its meaning). The step's name says which path.
- **FR-2 Edit and confirmed.** `context_confirmed` and the edit path read the window off the window page (Edit lands
  on 1 of 2 filled, *Continue*, 2 of 2 with the saved window) and hold the count and unit as today; `_save_context`
  presses the window page's Save.
- **FR-3 The readers and the gallery.** Any founder-screen anchor in `quality/readers/*.md` or `quality/rubric.py` that
  names the context form's five controls names the two screens; the gallery's recorded context screens (the examples
  as data) gain the window page; the marks' versions move only if a mark reads the form.
- **FR-4 Nothing else moves.** The wire, `instructions/`, the respondent legs, the other steps.

## Acceptance

`make unit` green with ZERO failed (master's counts as the last spec's tasks.md records them); on the local stack at
keel-web 141 and the current cloud, `make eval K=s005`, `K=s015` and `K=s016` (money alone, no window page) green;
the context screenshots in a bundle show both pages. Build on the founder's word of 2026-10-30, after keel-web 141
merges and after 096.
