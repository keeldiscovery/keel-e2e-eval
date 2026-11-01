# Spec 125 -- The referee follows keel-cloud 195 and keel-web 160 / 161

Three small mirrors the harness owes after today's builds. Builds on 124.

- **FR-1 Spelling corrected, words kept (keel-cloud 195).** The instructions now let the model write a misspelt word of
  the founder's in its dictionary spelling (*withot* -> *without*, *erros* -> *errors*); names and numbers never. The
  eval's `no_leak` vocabulary (`instructions/marks.py`, call (44a): the stems of the founder's typed words are subtracted
  from the leak list) reads a typed word and a served word as one word through a mirror of keel-cloud's
  `domain/vectors/Spelling.sameWord` (`src/main/java/com/keeldiscovery/cloud/domain/vectors/Spelling.java`): case-folded,
  equal, or both at least four letters, no digit in either, **same first letter**, within optimal-string-alignment
  distance 1 at four letters and 2 at five or more. A new `instructions/spelling.py` (`same_word`, `in_text`, `run_in`)
  with its own tests; `no_leak` is the only caller today. No mark number moves.
- **FR-2 The condition is heard before it is answered (keel-web 160).** On a lock since keel-cloud 194 the AI
  interviewer's sheet plays `clips.condition` on the condition step (`[data-testid=ai-sheet][data-step=condition]`,
  the stage's `data-clip`): the harness's AI walks wait for that clip (as they wait for the problem clip) before the
  chip's / screener's Yes / No; the decision-maker's AI link asks its screener after the opening; the counter counts the
  condition (*Question 1 of N*; the gate is 2). A lock from before 194 (no `condition` clip) is walked as before.
- **FR-3 The brand plate (keel-web 161).** The idea check shows `[data-testid=brand-plate]` with `brand-plate-mark`
  and `brand-plate-line` once the name is typed, and none before; the founder's walk asserts it where it asserts the
  idea check. On the stranger's idea card the first line is split around `[data-testid=idea-mark]` when the served
  line reads *Imagine {name}, {what}.* with a name of five words or fewer: a whole-line match reads the element's text
  (`.iv-ideacard__what`'s `textContent`), never a single text node; a bare *Imagine Fresco.* carries no mark.
- **FR-4** `make unit` green (`set -o pipefail`).

## Acceptance

`make unit` ZERO failed against keel-cloud 2d848360 and keel-web 2b84758. The next quality cycle's AI walk on a
re-locked payroll link hears the condition and answers it; a founder's walk sees the plate.
