# Tasks 098 -- The harness reads the group's URL off the section's `data-url`

Branch `098-the-group-url-off-data-url` (worktree `wt/keel-e2e-eval-098`), off master `075b9e1` (110's spec on top of
108's `925ae38`; the brief named `925ae38`). Built by Claude on 2026-10-30. Read only: keel-web at `426e23c` (142 merged
at `9c5d8d0`; `src/components/interviews/GroupSection.tsx`), keel-cloud-docs at `8c53497f`. **No stack, no browser
beyond the unit tests' local Chromium, no model, no paid call.** Nothing merged into master; the branch pushed after
every commit, never force-pushed.

| Commit | What |
|---|---|
| `bdacd45` | FR-1: `interviews_screens.groups()` reads `data-url`; `GROUP_LINK` retired; S-017's Sent step reworded |
| `bf25fca` | FR-1: `tests/test_open_link_092.py`'s pins, fixture and two new tests |
| the docs commit | this file and `AGENTS.md`'s spec-098 paragraph |

## Unit (the gate)

| | passed | failed | skipped |
|---|---|---|---|
| 108's tasks.md record, branch at `f5930d3` (keel-cloud-docs `4d790648`, keel-web `2332958`) | 4,186 | 1 | 53 |
| **master** `075b9e1`, the same four tests run against keel-cloud-docs `8c53497f`, keel-web `426e23c` | -- | **4** | -- |
| **branch at `bf25fca` (the last code; the docs commit adds none)** | **4,186** | **3** | **53** |

The +2 passed are this spec's two new tests; the 092 pin is cleared (master's one failure of the brief). **The three
left are not this spec's and are not fixed here** -- keel-cloud 170 (price version 14, the gate's chips, *I can't
recall*) merged on keel-cloud-docs master during this build (`2078a70d`..`8c53497f`), and keel-e2e-eval spec
`110-the-harness-reads-the-lock-jobs-frontier-tier` (written at `075b9e1`, not built) is the harness's half:

- `tests/test_credits_at_begin_088.py::test_the_mirror_is_keel_clouds_charge_table` (`14 == 13`, `charge.PRICE_VERSION`)
- `tests/test_corpus_r19.py::test_the_backtest_record_holds_every_served_item_to_the_spoken_form` (`9 == 10` items)
- `tests/test_instruction_spoken.py::test_the_corpus_record_keeps_every_rule_and_nothing_is_known_apart` (S6: the
  escape *I don't know* against the registry's *I can't recall*)

Master `075b9e1` fails all three against the same keel-cloud-docs (checked in this worktree, detached, then back);
nothing they read is touched by this branch. `make unit` run from the worktree, on its own `make venv`.

## FR-1 -- the url off `data-url`

- [x] T001 `harness/interviews_screens.py`: `GROUP_LINK` (`[data-testid='group-link']`) deleted; `SENT_GROUP` (`:161`)
  carries a comment naming the root's `data-group`, `data-closed`, `data-url`. `Interviews.groups()` (`:797`) reads
  `"url": section.get_attribute("data-url") or None` on every section, open or closed, and drops the `"link"` key (the
  addendum allows dropping it or keeping it as None; nothing read it). `GROUP_LINK_MADE` and the Send-more read
  (`:731`) are unchanged.
- [x] T002 `evals/open_link_leg.py`: the S-017 Sent step's title and the module docstring's item 7 say *its url* (the
  section's `data-url`) for *the link*; the assertion `section["url"] == ctx["url"]` (`:532`) is unchanged and now
  reads `data-url`. No assertion expected a shortened link or a closed group's `url is None`, so none changes.
- [x] T003 `tests/test_open_link_092.py`: `test_every_pin_the_harness_reads_is_in_136s_markup`'s `GroupSection.tsx` ids
  read `data-url=` for `group-link`; `SENT_HTML` puts `data-url` on the section and drops the `linkshort` span;
  `test_the_by_group_tab_is_read_as_136_draws_it` asserts the record has no `"link"`.
- [x] T004 New: `test_the_group_section_draws_no_link_and_keeps_its_url_on_the_root` (keel-web's source has no
  `data-testid="group-link"`, `data-url={group.url}` sits on the `<section>` root beside `data-group`, Copy's
  `text={group.url}`; the harness has no `GROUP_LINK` and no `group-link'` selector; `GROUP_LINK_MADE` as it was) and
  `test_a_closed_groups_url_is_read_off_its_data_url` (a closed section: url read, no Copy, Reopen, the empty line).

## FR-2 -- nothing else moves

- [x] T005 The open-link leg's arrival, sign-in, answered and inactive reads, the close / reopen steps and the marks are
  untouched (`git diff origin/master --stat`: three code/test files, the two docs).

## Not foreseen by the spec

1. **Master moved past the brief's `925ae38`** to `075b9e1` (spec 110's spec.md alone); the branch is cut from it.
2. **keel-cloud 170 merged during this build** and turns three unit tests red on master and on this branch alike
   (above); ZERO failed needs eval 110, not 098.
3. **The spec's FR-1 names `[data-group]`**; the code's selector is `SENT_GROUP` (`[data-testid='sent-group']`, the same
   element, per the addendum), so the read stays on `SENT_GROUP`.
4. **The closed-section check is a unit test only.** The addendum says the url is present when closed; FR-2 keeps the
   leg's close step as it was, so S-017 does not add an assertion on the closed section's url.
5. `make eval K=s017` (the acceptance's second half) brings the stack up and is the coordinator's, not run here.
