# Spec 124 -- The referee follows keel-cloud 194 (the condition's clip)

keel-cloud 194 adds `ClipKind.CONDITION` (the condition said aloud, *{question} Yes or no.*) and the clips map's
`condition`; keel-web 160 plays it. Builds on 123. Contract 57.

- **FR-1** `harness/interviewer_fake.py` `KINDS` gains `CONDITION`; the fake renders it as it renders `PROBLEM`.
- **FR-2** The walks that read the AI interviewer's clips (the hello-video / ai-interviewer journeys, the spoken-form
  checks in `instructions/spoken.py` where they enumerate clips) accept and, where they assert the served clips of a
  link with a condition, expect `condition`; a lock with none (an older bundle) is not refused.
- **FR-3** The problem passage's two sentences (keel-cloud 194 FR-2) where the harness pins the passage text.
- **FR-4** `make unit` green (`set -o pipefail`); the contract snapshot moves to 57 the way 56 did.

## Acceptance

`make unit` ZERO failed against keel-cloud 194.
