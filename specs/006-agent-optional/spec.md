# Feature Specification: S-002, the agent-optional day

**Feature Branch**: `006-agent-optional`

**Created**: 2026-09-04

**Status**: Draft — for the founder's review

**Input**: the founder's direction of 2026-09-04: a founder connects a runtime, creates a project,
logs out; later the runtime is not running and they log back in. Creating a *new* project must be
disabled — but everything else they own must still work: read the project, send interview links,
download the brief. "The local runtime is only needed to create a project or to infer the result."

## Why this is worth a scenario

S-001 proves the whole journey with the agent present throughout. It cannot catch over-gating —
a screen that disables itself because no agent is connected, when nothing about it needs one.
That failure is silent (the founder simply cannot do a thing they should be able to do), and the
product has already been read once against this question: keel-cloud gates exactly two founder
endpoints on a live agent, `POST /v2/projects` and `POST …/readings`, which is right. This
scenario pins that, and pins the UI to it.

## User Scenarios & Testing

### User Story 1 - The day without a runtime (Priority: P1)

Continuing from a project that already exists and has been approved through at least the problem
card, with invitations already sent and at least one answer already read:

1. **Log out.** Stop the runtime (`make` kills it by heartbeat pid, as `down` does).
2. **Log back in.** The landing shows **L4**: the project list, *New project* disabled, the reason
   beside it, and the agent line reading *No agent connected* with a *Connect* link. Every row is
   clickable.
3. **The project reads.** Open it: the approved cards render with their claims, beliefs and
   evidence; the side nav's stage words are as they were; nothing is disabled that only shows.
4. **Inviting still works, end to end, with no agent.** People → *Kinds of people* → *Send the
   questions* → the three-step popup, including the preview → *Generate the link* → the link is
   real. A participant opens it in an isolated context and answers.
5. **Reading is the one thing that is not offered.** Back on People, the new answer shows in
   *Their answer*; the *Your agent* column reads *Not read yet*; and the read action is **visibly
   unavailable with its reason** — not merely refused after a click.
6. **The brief still downloads.** Nav → *Brief* → the standing renders with the four lists and the
   people who were asked; the print layout renders (`emulate_media("print")`).
7. **Reconnect.** Run the connect skill again, approve the new device code in the browser, and the
   agent line goes green. The read action becomes available; use it; the toast names what moved;
   the card's verdict updates.
8. **And now a new project is allowed again**: back at the landing, *New project* is live.

**Independent Test**: the run above passes with no LLM, and at three points asserts the **wire**
beside the screen: with no live agent, `POST /v2/projects` answers `422 rule: agent`;
`POST /v2/projects/{id}/invitations` answers `201`; `GET /v2/projects/{id}/standing` answers `200`.

**Acceptance Scenarios**:

1. **Given** no live agent, **When** the landing renders with projects, **Then** it is L4: list
   present, creation disabled with a reason, rows clickable.
2. **Given** no live agent, **When** an invitation is created through the UI, **Then** it succeeds
   and the participant page it produces is answerable.
3. **Given** no live agent and an unread answer, **When** People renders, **Then** the read action
   is disabled and states why — the founder is never left to discover it by refusal.
4. **Given** no live agent, **When** the brief is opened and printed, **Then** both render.
5. **Given** the runtime is reconnected, **When** People renders, **Then** the read action is
   available, and using it moves the card.
6. **Given** no live agent, **When** `POST /v2/projects` is called directly, **Then** `422` with
   `rule: "agent"` — the UI's lock is the experience, this is the guarantee.

### Edge Cases

- **The scenario needs a project that already exists.** It runs after S-001 in the same stack
  session where possible; otherwise it builds its own prelude by driving S-001's first two steps
  with the runtime up. The prelude is a helper, not a second copy of S-001.
- **Logging out closes the keel session; the runtime keeps polling** (spec 020 US3). This scenario
  stops the runtime *before* logging back in, so the new keel session has nothing to bind.
- **Reconnecting mints a new device authorization** — the old one is spent. Step 7 runs the skill
  script fresh.
- **The stale toast**: a completion toast from before the logout must not reappear after login.
- Runs on the **playground** profile by default, like S-001, so two operators never collide.

## Requirements

- **FR-001** `evals/test_s002_agent_optional.py`: US1 steps 1–8 with `§` citations for the moments
  it touches (§1.0 arrival, §1.4 inviting, §1.5 waiting, §1.6 reading, §1.10 the brief) and the
  three wire assertions.
- **FR-002** `harness/connect.py`: `stop_runtime(config)` (heartbeat pid, as `stack/runtime.py`
  does) and a `reconnect` helper that reruns the skill script and returns the new code.
- **FR-003** `harness/browser.py`: `Landing.new_project_locked_reason()`, `People.read_action_state()`
  (returns enabled/disabled plus the reason text), and whatever else steps 3–8 need — added, not
  reshaped.
- **FR-004** The prelude helper `evals/preludes.py: approved_project_with_one_read(...)`, shared
  with S-001 if it can be without contorting either.
- **FR-005** `canon/CANON.md`'s ledger gains S-002 beside S-001 on §1.4/§1.5/§1.6/§1.10 — *(the
  ledger edit is keel-cloud's, made by the founder's session; the referee never edits a product
  repo)*.

## Success Criteria

- **SC-001** `make eval K=s002 PROFILE=playground` green from a stack S-001 has already run in,
  and green from cold with its own prelude.
- **SC-002** Scored under policy v6 like S-001; a run bundle with screenshots per step.
- **SC-003** Any over-gating found is a `runs/DRIFT.md` entry with the screen and the wire
  evidence side by side — never worked around in the harness.

## What I expect this to find (stated in advance, so the scenario is not written to pass)

Read against the built screens before writing this: keel-web's People page never consults the
agent state at all. The read action is disabled only by `unreadCount === 0`, so with an unread
answer and no runtime it will be **offered**, clicked, and refused by the wire — and the refusal
is not rendered anywhere on that screen. If that is what the run shows, it is US1 scenario 3
failing, and the fix belongs in keel-web: disable the action and say why, the same way the
landing's *New project* does.
