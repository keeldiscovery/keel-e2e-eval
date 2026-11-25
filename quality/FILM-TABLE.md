# The film, judged

Bundle `20261125T012454Z-film-walk` · FILM_RUBRIC_VERSION 1 · the film reader claude-opus-5-5 medium (anthropic api) · the founder-reader claude-opus-5-5 medium (claude CLI) · the bar 80% (`quality/cycle.toml` [film] film_bar_pct) · spec 163.

**This round**: mean film_pct 37.5 over 1 entry; 0 pass, 1 fall short (09-karsa); the round **fails**. Holdout tabled: 09-karsa; holdout short: 09-karsa.
**Dollars**: the reading $0.57, the walk $0.85.

## The table

| entry | F1 | F2 | F3 | F4 | F5 | F6 | F7 | F8 | film_pct | flagged | founder_pct | §A score_pct | §B after_pct | $ | passes |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 09-karsa (holdout) | 0 | 1 | 1 | 1 | 1 | 0 | 1 | 1 | 37.5 | yes | 87.5 | -- | -- | 0.57 | no |

§A and §B are `make read-screens` on **the film's project** (spec 165: the one project an entry -- the film told, locked, its link answered by the entry's people, its page read after them): §A the strangers' screens of the film's link (RUBRIC.md R1-R6, and §G), §B the founder's page after the answers (the Overview's cards, the Insights tab, the brief); `--` where it has not been read. No typed project's score is tabled here. The solution film's column joins once the solution batch is walked.

## Weak criteria

- **F1** (problem): mean 0.00, a 0 in 1 entry (09-karsa) -- `make film-advise` proposes a rule for it.
- **F2** (problem): mean 1.00, a 0 in 0 entries -- `make film-advise` proposes a rule for it.
- **F3** (problem): mean 1.00, a 0 in 0 entries -- `make film-advise` proposes a rule for it.
- **F4** (problem): mean 1.00, a 0 in 0 entries -- `make film-advise` proposes a rule for it.
- **F5** (problem): mean 1.00, a 0 in 0 entries -- `make film-advise` proposes a rule for it.
- **F6** (problem): mean 0.00, a 0 in 1 entry (09-karsa) -- `make film-advise` proposes a rule for it.
- **F7** (problem): mean 1.00, a 0 in 0 entries -- `make film-advise` proposes a rule for it.
- **F8** (problem): mean 1.00, a 0 in 0 entries -- `make film-advise` proposes a rule for it.

## Each entry's whys

### 09-karsa -- film_pct 37.5, flagged

- F1 0: No picture was served for any scene, so the viewer never sees the saver in shalwar kameez on the family sofa in the evening with phone, rupee notes and tea; the person and setting are absent. -- *instead*: Scene 1: draw the saver in a plain shalwar kameez and shawl on the sofa of a modest home in the evening, phone in hand, a small stack of rupee notes, notebook and tea on the table, fan overhead.
- F2 1: Line 2 says the task (turning leftover rupees into dollars to keep their value), but no picture shows it arriving. -- *instead*: Scene 2: show the saver counting the leftover rupee notes and looking at the phone, deciding to change them into dollars before they lose value.
- F3 1: Line 3 names the exchange companies and Binance, but no scene shows the saver at an exchange counter or using Binance on the phone. -- *instead*: Scene 3: show the saver handing rupee notes across an exchange company counter, then a phone with a blank trading-app screen held like a bank account.
- F4 1: Each of the three limitations (no foreign currency account, rationed dollars, the Binance premium) has its own line and none is invented, but none is shown, because every scene has no picture. -- *instead*: Scenes 4-6: a bank clerk shaking his head behind a closed window; an exchange counter giving back only a thin slice of what was asked; the phone app taking an extra orange-tinted slice off each coin.
- F5 1: Line 7 says the savings shrink, but no slumped person is shown, and it drops the founder's cause and size (20-30% a year lost to inflation). -- *instead*: Scene 7: show the saver slumped on the sofa beside a shrinking, toppling stack of notes, with the line 'Inflation eats 20-30% of your savings every year.'
- F6 0: The lines are short, plain and single-minded, but every scene has no picture, so not one line matches a picture. -- *instead*: Serve a picture for every line so each caption sits over the scene it names, e.g. 'Banks will not open a foreign currency account for you' over the bank clerk refusing.
- F7 1: The beats run in order (who, task, today, three shortfalls, cost, ask) with chapter marks in place, but the cost beat is thin without inflation and the 20-30% a year. -- *instead*: Line 7: 'Inflation eats 20-30% of your savings every year.' This gives the cost beat its cause and size.
- F8 1: With no pictures there is no stray text inside a picture, but the rendered frames were not available, so caption fit on the phone and laptop frames cannot be confirmed clear. -- *instead*: Render every scene with its picture and check that each caption sits fully inside the clear bottom third on both the phone and laptop frames.
- missing: the person (saver on the family sofa, evening) not shown; the task (turning leftover rupees into dollars) not shown; today's way (exchange company counter / Binance on the phone) not shown; banks refusing a foreign currency account not shown; exchange companies rationing dollars not shown; Binance premium on every dollar not shown; the cost (savings losing 20-30% a year to inflation) not shown and the inflation figure not said

## Findings for DRIFT

- 09-karsa (F1): the person or the setting is not this person's (another trade, another place, or a named company) -- no frame
- 09-karsa (capture): the build ended 'failed' (failedScene 7: Your savings shrink.) -- no frame

`make read-film-table RUN=... DRIFT=1` appends them to `runs/DRIFT.md` in its shape.
