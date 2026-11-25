# Spec 168 -- The judge presses the lock's retry once, and the stub founder answers each limitation in the entry's words

The run on five (bundle `20261125T084949Z-film-walk`, cloud `c7079b59`, web `336eb477`, eval `36efa18`): two of the five
problem legs never sent a link. Their PROBLEM calibration read `FAILED` with three questions written and answered: the
calibration writer's result was refused by a window-frame rule (E9 on one entry, E7 then E2 on the other), repaired
once, refused again -- the product's one repair turn (keel-cloud spec 107) -- and `lock_project` raised `LockFailed` at
step 2. A founder on that screen sees FounderVoice's retry (keel-web 230, keel-cloud `POST calibration/{vector}/retry`)
and presses it; the walk does not, so the judge lost two entries' strangers (§A, §B empty) and the solution leg on one.
`lock_project` already retries the questionnaire once at step 5; the calibration at step 2 gets the same. On the same
run the two solution builds that ran to the reviewer failed at `solves` (keel-cloud 276 fixes the draft); the stub
founder's part in it is `harness/film_frames.py`'s beat 3, which answers every limitation with the stock clause *{Limit}:
{name} takes care of that.* -- words no entry says, and words the reader marked S7 0 on the lineman's film (*reads as if
Voltair does 50-150 poles a day*). Built on master with 167 merged (`36efa18` or later); small; nothing paid.

## Rules
- **FR-1 The calibration retried once.** `harness/film_strangers.lock_project` step 2: where `GET calibration/{scope}`
  reads `state: FAILED`, the walk presses `POST /v2/projects/{id}/calibration/{scope}/retry` once (the founder's
  FounderVoice retry) and waits `calibration_wait_s` again for READY; `record["calibration_retried"]` true; a second
  `FAILED` (or the retry refused, `QUESTIONS_NOT_FAILED` aside) raises `LockFailed` at the same step with
  `retried: true` in its detail. The solution leg's lock (`run_film.py` ~755-796, scope SOLUTION) goes through the
  same function and gains the same retry.
- **FR-2 The retry recorded and tabled.** `film.json` / the solution's record carry `lock.calibration_retried`;
  `quality/film_reader.py` (or the table writer) adds a DRIFT finding on the entry *(capture): the lock's calibration
  was written again on the founder's retry* with the entry's film frames as the link (no frame on the solution's
  where none); `FILM-TABLE.md`'s entry heading says *lock retried* beside *flagged* where it was. The run's score
  files carry `measures.lock_retried: true|false`; the *Compared with* section is unchanged.
- **FR-3 The limitations answered in the entry's words.** `harness/film_frames.py`'s beat 3 (166 FR-1): each
  limitation's clause is *{Limit}: {name} {mechanism}.* -- the limitation as the problem story said it, then the
  brand's name and the entry's `solution_mechanism.mechanism` as a bare clause (`_bare_end`), the same clause for
  every limitation of the entry (one rule for every entry; the entry holds no answer per limitation and none is
  invented). The stock *takes care of that* is gone. `then[3]` unchanged. `idea_beat_faults` holds the clause under
  the spoken-form caps as today. The fixtures that pin beat 3's words re-cut.
- **FR-4 Tests.** `tests/test_the_strangers_on_the_films_link_165.py`: `lock_project` on a stub `call` whose
  calibration reads FAILED then READY after the retry (the retry POSTed once, `calibration_retried` true); FAILED
  twice raises at step 2 with `retried: true`; READY first time POSTs no retry. `tests/test_the_solution_film_judged_166.py`:
  beat 3's clauses name each limitation and the mechanism, never *takes care of that*; the DRIFT line and the table's
  *lock retried* mark from a record with `calibration_retried`. `make unit` green on the base's known reds only.
- **FR-5 The respondent-question rule.** The stub founder's beats are typed to keel-cloud 271's four questions and
  end up spoken to respondents on the film: the words keep the AI-avatar spoken-form guidelines (one wording, short
  sentences a listener follows once, no placeholder, no number the entry does not say).

## Acceptance
- On a stack whose calibration writer fails once and passes on the retry, the walk sends the link and the strangers
  walk; the table marks the entry *lock retried* and DRIFT gains the finding.
- The language learner's beat 3 reads *A tutor is hard to schedule: Issen holds a spoken conversation with an AI tutor
  that adapts to their level, goals and interests.* (the entry's mechanism), and so for each limitation.
- Nothing paid: `DOOR=fake` and unit tests only.
