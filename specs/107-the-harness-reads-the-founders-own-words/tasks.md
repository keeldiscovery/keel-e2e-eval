# Tasks 107 -- The harness treats the founder's own words as not jargon, as keel-cloud 175 does

Branch `107-the-harness-reads-the-founders-own-words` (worktree `wt/keel-e2e-eval-107`), off master `a0ddf77` (105
merged). Built by Claude on 2026-10-30. Read only: keel-cloud-docs at `4d790648` (175 merged: `Vocabulary.typedIn`,
`RevealWords.m5` / `jargon` with the founder's texts, `VectorCorridor.founderTexts()`) and its
`specs/175-.../tasks.md` *The keel-e2e-eval pins that must move*, the checklist below. **No stack, no browser, no
model, no paid call.** Nothing merged into master; the branch pushed after every commit, never force-pushed.

| Commit | What |
|---|---|
| `c9cbe20` | not in the spec: `.venv` untracked (below) |
| `3af1824` | FR-2 / FR-3: the M5 mirror, `plain_line`, `LOCK_PLAIN_WORDS`; `test_after_131`'s re-pins |
| `ee3bb26` | FR-1: the J1 mirror and the golden walk's strict check |
| `90bbca6` | FR-2: the problem sentence's M5 check (SC4) |
| `3f0819b` | FR-5: `tests/test_founders_own_words_107.py` |
| the docs commit | this file and `AGENTS.md`'s spec-107 paragraph |

## Unit (the gate)

| | passed | failed | skipped |
|---|---|---|---|
| 105's tasks.md record, **master** `a0ddf77` | 4,143 | 0 | 53 |
| branch at `90bbca6` (the code, before the new tests) | 4,143 | 0 | 53 |
| **branch at `3f0819b` (the last code; the docs commit adds none)** | **4,166** | **0** | **53** |

The +23 are `tests/test_founders_own_words_107.py`; none removed. `make unit` run from the worktree with `stack.toml`'s
`keel_cloud` at keel-cloud-docs `4d790648`.

## The checklist (keel-cloud 175's *eval pins that must move*)

- [x] T001 **The founder's texts and the match** (`instructions/corpus.py`): `founder_texts(entry, audience_words=())`
  mirrors `VectorCorridor.founderTexts()` -- the context's typed fields (`FOUNDER_CONTEXT_FIELDS`: actor, job,
  circumstance, segment), `statements.problem`, `statements.solution` (whitespace folded, as `founder_inputs` types
  them) and the audience words; never Keel's interpretations. `typed_in(word, texts)` mirrors `Vocabulary.typedIn`:
  whole, case aside, a letter / digit / hyphen either side is no boundary (`_word_pattern`), no stemming.
- [x] T002 **J1** (FR-1): `harness/vectors_script.py` `expected_j1(entry, audience_words=())` leaves out the audience
  words and every jargon word typed in the founder's texts. 05-paidly's seed says *A platform that pays the translator
  ...*, so it owes no note; `evals/corpus_scenario.py`'s strict J1 check (`:1520-1526`) hands the idea's served
  `audienceWords` to the mirror and its comment now says the card carries none.
- [x] T003 **M5** (FR-2): `m5_faults(lines, audience_words=(), founder_texts=())` skips a typed M5 word; the names in
  parentheses and the design note read the line alone, as 175 T003 keeps them.
- [x] T004 **`plain_line`** (FR-2): reads `founder_texts(entry, audience_words)` itself (the walk already passes the
  entry), so it never moves a typed word -- not by a row, not by the fix's suggestion, not by `PLAIN_FALLBACK`.
- [x] T005 **`LOCK_PLAIN_WORDS`** (FR-2): every row kept; a row fires only where no M5 word it carries is typed
  (`_row_fires`). On the entries' own texts: 10-palus fires only *mortgage-backed bonds* (not its seed's), 14-code-four
  only the singular *check word* (no stemming), 11-issen / 12-transload / 21-codyco none, 16-pairio all five (pinned).
- [x] T006 **The problem's sentence** (FR-2): `evals/scope_marks.py` `sentence_faults(text, founder_texts=())` skips a
  typed M5 word; SC4 reads the record's `founder_texts`, which `evals/scope_journey.py` `record_of` keeps (the entry's
  texts, and on money alone the idea's audience words).
- [x] T007 **The breach text** (FR-3): no harness test matches a whole word-fault text; the synthetic refusals in
  `test_three_stops_096`, `test_after_130`, `test_after_131` read the unmoved prefix and stand.
- [x] T008 **Re-pinned, with why** (FR-3): `tests/test_after_131.py` walked founder-typed words to a refusal and an edit
  (Codyco's *PMS*, Transload's *3D box* and *workflow*, Code Four's *check words*, Palus's bond words). 175 never refuses
  them, so each is now walked on the entry with those words cut from its own texts (`keels_words`), the words Keel's --
  keel-cloud's own pattern for Karsa (*a Karsa seed without the two trade words*). No assertion removed.
- [x] T009 **Nothing else moves** (FR-4): `evals/interviewer_leg.py:780` (`>= 22`) stands; the judge, the quality
  record, the marks (`MARKS_VERSION`, `SCOPE_MARKS_VERSION`) and the word lists are untouched. Fewer `lock_refused`
  findings on a back-test walk are the point, not a regression.
- [x] T010 **Tests** (FR-5): `tests/test_founders_own_words_107.py` (23): `typed_in`, `founder_texts`; `expected_j1`
  on 05-paidly (none) and on a Paidly seed without *platform* (the note, and the audience-word exemption); every golden
  card owes none; `m5_faults` on 10-palus's card in its own words (none; the lists alone still trip three) and with an
  added *API* (one fault, on *API*); the spoken-form rules on Codyco's typed parenthesis; the M5 words each back-test
  seed types; the rows that fire; `plain_line` and a refused lock answered on *API* alone; `sentence_faults` keeping
  Palus's *money market* and still faulting *sweep account*.

## Where the spec and the code differ (the code's patterns followed)

- **The typed context fields are four.** 175 reads `ContextFields`' five (with *occasion*); keel-web's context form
  types four (`vectors_screens.Corridor.context`) and the walk never types an occasion, so the cloud's occasion is
  empty on every walked project and the mirror reads the four.
- **A row "fires only on a word the entry did not type" is read through the M5 words it carries.** A row is a phrase
  (*fits a 3D box to it*), not a word: it is skipped where an M5 word in it is typed. 16-pairio's list rows (*SAP,
  Maximo or SharePoint*) are typed too but carry no M5 word -- the list of names is a spoken-form rule the cloud still
  refuses (175 T003, its *did not foresee* 5) -- so they keep firing, beside its *CMMS* / *ERP*.
- **The audience words**: the cloud's J1 and M5 exempt them twice (the exact set and inside `founderTexts`); the mirror
  does the same. `expected_j1` took an optional `audience_words` so the strict check reads what the wire served.

## Not foreseen by the spec

- **Spec 105's first commit tracked a `.venv` symlink.** `8147930` committed the 105 builder's worktree link
  (`.venv -> /Users/.../keel-e2e-eval/.venv`); `.gitignore`'s `.venv/` matches a directory only. Fast-forwarding the
  main checkout to `a0ddf77` (20:06 ET) replaced its ignored venv directory with that link, which points at itself, so
  **the main checkout has no venv** (`make unit` there would fail on `.venv/bin/python`). `c9cbe20` untracks the link
  and ignores `.venv`; once merged the main checkout needs `make venv` (it rebuilds from `requirements.txt`). This
  build ran on a venv made in the worktree.
- `scope_journey.problem_sentence` (the mirror of `ProblemSentence`'s cut) does no M5 read today, so nothing moved
  there; SC4's `sentence_faults` is where the M5 read is held.
- **For the coordinator** (brings the stack up; the founders on fakes): `make eval K=s005`, 05-paidly's golden journey,
  with `stack.toml`'s `keel_cloud` at keel-cloud-docs master past 175.
