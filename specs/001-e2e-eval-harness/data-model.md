# Data Model: E2E Eval Harness

## stack.toml
`[paths] keel_cloud|keel_web|keel_skill` (defaults ../…) · `[ports] postgres=55432,
cloud=18080, web=5173` · `[timeouts] cloud_boot=120, web_boot=60`

## Transcript entry (transcript.jsonl)
`{seq, ts, kind: protocol|browser|assert|note, name, party: agent|founder|participant|stack,
request?, response?, screenshots?: [file], ok: bool, error?}`

## Run bundle (runs/<timestamp>-<scenario>/)
`transcript.jsonl` · `screenshots/NNN-slug.png` · `versions.json` (four repo commits + dirty
flags) · `verdict.json` ({scenario, passed, failed_step?, duration_s}) · `report.html`
(self-contained, inline thumbnails) · on failure: `failure/page.html`, `failure/console.log`

## Scenario (evals/scenario.py)
- `name`, `slug`
- `payloads`: mapping issuance→builder — opportunity(stage), roles(stage), assumptions(stage),
  interpretation(invitation, responses)
- `answers`: participant answer table per assumption (support|contradict|skip + free text)
- `about_line`: what the founder types on the invite screen
- assertions are plain code in the test using the step API

## FounderAgent state
`project_id`, last `revision`, facts store (payloads already submitted — reused on
concurrency), current issuance {action, token, context[], submissionSchema, detail}
