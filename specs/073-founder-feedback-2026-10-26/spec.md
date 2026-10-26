# Spec 073 -- The harness follows keel-web 113 and 114 (the founder's staging review of 2026-10-26)

After keel-web spec 113 (the context step: Save → the wait → the *Keel understands* card → Edit back to the form; *A
word from you* hidden behind a flag; the AI player's crop for a landscape-picture face; the Overview card's lead gone)
and spec 114 (the welcome clip per scope). No marks change unless named; REVISION 16.

## Rules

- **FR-1 The context step's flow.** The founder's and the corpus walks press Save, hold the wait (the timer and the
  stat cards), read the card as the transformed context, and where a walk edits the context it presses *Edit* and
  gets the form back filled; the selectors from keel-web 113's tasks.md. The four states are asserted on S-005 (the
  Countly walk).
- **FR-2 *A word from you* is not walked.** The last step starts on its first visible screen; the problem study's last
  step is *Who asks the questions* alone (no *1 of 2*); the pitch the walks typed is dropped from the scripts and the
  thank-you's default words are asserted on the respondent's last screen; marks that counted the word screen are
  re-pinned (say which).
- **FR-3 The Overview card's lead.** The Overview assertions stop expecting the panel lead line (`rp-plead`) on the
  full Overview and keep it on the brief's page one; the stage rows carry the state as before.
- **FR-4 The welcome per scope.** S-015 (problem) and S-016 (money) assert the welcome sheet's clip key for their
  scope (`welcome-problem`, `welcome-money`) and the guide marks (G-series) count the four new clips; S-005/006/007
  under ALL keep `welcome`.
- **FR-5 The player's crop** is not asserted beyond the page's own classes on the phone walk (the frames are keel-web's).
- **FR-6 Nothing else moves.**

## Acceptance

`make unit` green; the six journeys (S-005/006/007/014/015/016) green on the local stack with keel-web 114 merged.
