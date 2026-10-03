"""S-012 -- the journey through a host (specs `016-copilot-e2e`, `019-journey-through-a-host`,
`021-short-journey` and `024-keels-ai-cell`).

**Live**, opt-in through `make eval-live K=s012`, never part of `make eval`/`make eval-all`, and it
spends the founder's own money on whichever host it is pointed at.

**One scenario, two hosts.** `KEEL_JOURNEY_HOST` (set by `make eval-live K=s012 HOST=claude|copilot`,
default `copilot` so the command that produced the spec 016 run of record still means what it
meant) decides which. keel-cloud `canon/designs/e2e-matrix-design.md` §5.1 is why: the matrix's
three axes are an OS, a Python and a **host**, and *"the scenario each cell runs is S-001, the
founder's journey, through the host"*. A scenario that existed for one host could only ever fill a
third of the grid.

What differs between the two hosts is a handful of flags, one environment variable and the way
each CLI prints what it knows -- all of it behind `harness/agent_host.py`. What does not differ is
everything below: the same legs, in the same order, asserting the same shapes, on the same wire.

**...and one of the four is not a host at all** (spec 024). keel-cloud
`canon/designs/ai-credits-design.md` §6: *"The door decides the AI."* A founder who signs up with
Google at keel-web's `/signup` runs on **Keel's** AI -- nothing to install, no skill to load, no
*"keel connect"* to say, no device to approve and no runtime anywhere -- and keel-cloud answers
every job in process on its own Anthropic account (keel-cloud specs 044 and 045). So
`HOST=keel` **skips leg one entire** -- skipped, never asserted loosely: `harness/keel_host.py`
raises from every one of its host-leg methods, so an edit that reached for one gets a sentence
rather than an empty result that would read as a pass -- and asserts instead the six things only
that door shows: `1,500 credits available` on the shell line and **no** agent line,
`aiPath: "KEEL"` on the wire, a balance that drops the moment the first framing is held,
`execution.host: "api"` with a present, non-zero `actual_cost_micro_usd` on every job, the
founder's screens reading *Keel* rather than *your AI*, and a `KEEL_HOME` still empty when the
brief is written. Leg two is the same leg two: the founder's journey is the founder's journey
whichever AI is answering it.

It is also **the only run in this repository that spends the company's money** rather than the
founder's own plan -- about 1,250 credits, $12.50 at list price and about $2.44 of actual
inference (design §6.3) -- which is why `matrix/cells.py` buys it once a Saturday and refuses it
in `per_change` by name.

Two legs, one runtime, and the runtime is what joins them -- on three of the four doors.

**Leg one, the host.** keel-connect-skill's plugin is installed into a **fresh host home**
(`CLAUDE_CONFIG_DIR` / `COPILOT_HOME`) from the real public marketplace with that host's own two
commands, the CLI is asked whether it can see `keel-connect` and whether it came from the plugin,
and then the founder's three words -- *"keel connect"* -- are said to `claude -p` / `copilot -p`.
Everything after that is asserted against the **runtime's own artefacts**, never the host's prose:
the heartbeat file in state `awaiting_approval`, the launch log's `KEEL_USER_CODE=` and
`KEEL_VERIFICATION_URI=` lines, and the eval cloud's own answer to
`GET /v2/device-authorizations?user_code=`. A host that said *"Keel is connected!"* and started
nothing would pass a grep of its reply and fails every one of these.

**Leg two, the thinker.** That same runtime is on **that host's executor**, because the skill told
it so -- Copilot by `SKILL.md`'s one `--host copilot` line, Claude by the skill's own host
detection -- and nothing in this scenario passes an executor of its own; `source=flag` is asserted
beside the name, because a runtime that guessed right off a `PATH` would prove nothing about the
skill. Then the founder's journey from S-001's own legs, with the host's model answering every
screen: three stages framed, reviewed and approved as-is, the entry's first five people invited
and answered (`KEEL_JOURNEY_PEOPLE`, default five on `full`, always one on `short` -- the founder,
2026-09-13: *"increase it to five, so that I see a completed brief"*; the product calls a line
*Too few to call* under five people), the reading read, *What this says* written, the overview and
one card opened.

**Every card assertion is a shape or an absence** (spec 008's judgement call 8, and spec 016
FR-007). A live model's sentence is not stable and a test that pinned one would be measuring the
weather; what is asserted is that the card exists, carries numbered lines, separates at least one
deal-breaker, and was not refused.

**Two lengths, and the short one is what every qualifying change runs** (spec 021).
`KEEL_JOURNEY_LEGS=short` (`make eval-live K=s012 HOST=... LEGS=short`) stops the journey after the
**first model job** -- the host leg entire, then the PROBLEM frame's confirmation card landing --
and leaves by the same door. It asserts exactly the assertions the full journey makes up to that
point and **not one thing more**: nothing is read out of the model's prose that was not read out
of it before, and no new shape is claimed because the run is shorter. `full` is unchanged and is
what the nightly and weekly sets run. The bundle's own name carries the difference.

**The founder is a golden-corpus founder** (spec 021). `KEEL_JOURNEY_ENTRY`, default `03-lullaby`,
names an entry in keel-cloud's `canon/designs/measured-beliefs/corpus/`; the entry's title is the
project name, its market is the market, its three statements are typed verbatim, and its **first
person** answers with their own story text and their own picks. They are read through
`harness/corpus_script.py` -- the same `founder_inputs`/`person_inputs` the six scripted scenarios
read them through, reused rather than copied, so the journey's founder and the corpus scenarios'
founder are the same founder rather than two people who happen to agree. What this does **not**
change is the model's half: the beliefs, the roles, the anchors and the pick lists on a live run
are the host model's own, so the person's story goes into the anchors the model wrote, in order,
and their picks are used where the model's own option list happens to offer them. Which is which
is recorded in the bundle, never asserted (spec 016 FR-007).

**Not scored.** No attribute of `evals/policy.py` applies to a scenario about which host loaded a
skill and which model answered a job -- the same reason S-008 and S-009 are not scored. The
evidence is the transcript, the two host transcripts beside it, and the per-job envelopes.

The referee owns no product code: a fault here is a `runs/DRIFT.md` entry, never a workaround.
"""

from __future__ import annotations

import json
import os
import re
import subprocess
import shutil
import time

import pytest

from evals.preludes import create_project, own_ai_door
from harness import (agent_host, canary as canary_mod, corpus_script,
                     keel_host as keels_ai, refusals, stranger_stories)
from stack import remote
from harness.browser import (INTERVIEW_BEGIN, INTERVIEW_CONTINUE, INTERVIEW_DONE_TITLE,
                              INTERVIEW_HEAD_WHAT, Auth, Chat, Connect, Landing, OpenedCard,
                              Overview, ParticipantPage, People, PrintPage, ReviewCard, Shell)
from harness.evidence import finalize_run, write_block, write_generated, write_host
from harness.steps import Recorder
from instructions import models as models_mod
from stack import runtime as stack_runtime

pytestmark = pytest.mark.live

#: **Which host this run is the journey through**, resolved once, at import, from
#: `KEEL_JOURNEY_HOST`. An unknown value raises rather than falling back: a typo that quietly ran
#: the other host would spend the founder's money on a measurement nobody asked for.
HOST = agent_host.journey_host()

#: **True when this run is the journey through Keel's own AI** (spec `024-keels-ai-cell`;
#: keel-cloud `canon/designs/ai-credits-design.md` §6: *"The door decides the AI"*). Read from the
#: host axis and nowhere else, so the door is chosen the same way the host is and by the same
#: command. It is the only flag in this file, and it turns off exactly one thing -- **leg one** --
#: and turns on six assertions that are only true behind the Google door. Leg two is untouched:
#: the founder's journey is the founder's journey whichever AI is answering it.
KEELS_AI = not agent_host.has_a_cli(HOST)

#: How often, on the Keel door, a wait on the screen stops to ask the wire whether the door is
#: bolted (spec 024 FR-010). Thirty seconds, not three hundred: `LLM_UNAVAILABLE:
#: KEEL_AI_DISABLED` is answered by keel-cloud **before a socket is opened** (keel-cloud spec 045
#: FR-032), and a run that waited five minutes for it and then reported a timeout would be
#: reporting the referee's own patience instead of the product's own sentence. Only this door
#: chunks its wait; the three CLI hosts wait exactly as they waited before, in one call.
NAMED_REASON_POLL_S = 30.0

#: **The Keel door's own job-wait ceiling** (`AgentHost.keels_ai_job_wait_s`; spec 024 FR-010,
#: measured on the staging twin, run 36625025566, 2026-09-29): keel-cloud's own job-timeout
#: abandonment for the assumptions job behind a stage's review card, and for the BRIEF job behind
#: *What this says*, moved from 300s to 600s there, so the waits that used to fit inside 300s need
#: to fit inside 600s instead. Read off the host object, exactly as `EXECUTOR_FOR_HOST` and every
#: other per-host fact this scenario asks for, rather than an `if HOST == "keel"` beside each wait
#: -- 480s for the three CLI hosts (unchanged; none of their jobs run against that clock), 660s for
#: the Keel door.
KEELS_AI_JOB_WAIT_S = agent_host.host_type(HOST).keels_ai_job_wait_s

#: **How long the founder waits for the project's one questionnaire** (spec
#: `026-journey-one-questionnaire` FR-005; keel-cloud spec 048).
#:
#: Since 048 the questionnaire is the **project's**, not a stage's, and it is written by one
#: `QUESTIONS` call that keel-cloud starts when the last framed stage is approved. So there is a
#: gap -- minutes, not milliseconds -- between the founder approving their last card and People
#: unlocking, and this is how long the journey is prepared to sit in it.
#:
#: **420 s on the three CLI doors**, and it is keel-cloud's own arithmetic rather than a guess: the
#: `QUESTIONS` job's abandonment deadline is **PT300S**, and two minutes are added for the queue,
#: the hand-off to the runtime and this poll's own 3-second granularity. The call itself is
#: estimated at ~18 s on Haiku 4.5 (`assumptions-step-design.md` §6.4) and measured at one to three
#: minutes against a live host, so the ceiling is about three times the worst measurement.
#:
#: **The Keel door's own number instead, read off the host object** -- 660 s, because keel-cloud
#: moved its in-process job abandonment from 300 s to 600 s there (spec 024 FR-010, measured on the
#: twin, run 36625025566). Read the way `KEELS_AI_JOB_WAIT_S` itself is read, and never written as
#: an `if HOST == "keel"` beside this wait: per-host facts belong to `harness/agent_host.py`.
QUESTIONS_WAIT_S = KEELS_AI_JOB_WAIT_S if KEELS_AI else 420.0


def _environment_of(base_url: str) -> str:
    """What keel-runtime's `status.environment` says for a base URL (its `config.environment_for`):
    `host:port` when the URL carries a port, the bare host otherwise. Mirrored here rather than
    imported so the referee never imports the runtime it is judging."""
    from urllib.parse import urlsplit
    parts = urlsplit(base_url)
    host = parts.hostname or ""
    if ":" in host:
        host = f"[{host}]"
    return f"{host}:{parts.port}" if parts.port else host

#: **How much of this journey is run**, resolved once, at import, from `KEEL_JOURNEY_LEGS`
#: (spec 021). `short` is the host leg plus the first model job; `full` is everything. An unknown
#: value raises for the same reason an unknown host does -- one typo either overspends or
#: underspends the founder's money and files the result under the wrong name.
LEGS = agent_host.journey_legs()

#: True when this run stops after the PROBLEM frame's confirmation card. Read in exactly two
#: places below -- where leg two would go on, and where the bundle records what it did -- so the
#: short journey is a *stopping point* in the one story and never a second story.
SHORT = LEGS == "short"

#: **Whose founder walks it** -- an entry id in keel-cloud's golden corpus (`KEEL_JOURNEY_ENTRY`,
#: default `03-lullaby`). Resolved at import beside the other two axes; the entry itself is read
#: inside the test, where the stack fixture has told us where keel-cloud is.
ENTRY_ID = agent_host.journey_entry()

#: **How many of the entry's people are invited and answer** (`KEEL_JOURNEY_PEOPLE`; five on the
#: full journey, always one on the short one, which never reaches the People page). Five is the
#: product's own *Too few to call* threshold, so the brief at the end has a verdict to say.
PEOPLE = agent_host.journey_people(LEGS)

#: `runs/<stamp>-s012-journey-<host>[-short]/`. The matrix uploads one bundle per cell and a reader
#: looking at eighteen of them has only the name to go on until they open one.
INSTALL = agent_host.journey_install()
BUNDLE = agent_host.bundle_slug(HOST, LEGS, INSTALL)

#: The founder's own three words. Not "run the keel connect skill", not "use the keel-connect
#: plugin to start the runtime" -- the point of leg one is that a host with the skill installed
#: recognises what a founder would actually type, and `SKILL.md`'s own description is what has to
#: do the recognising.
THE_FOUNDER_SAYS = "keel connect"

#: **C-5's pin, exercisable for the first time -- and load-bearing.** keel-runtime spec 005
#: measured on 2026-09-09 that CLI 1.0.83 refused every slug offered to `--model`, so
#: `CopilotExecutor.model` defaults to `None` and C-5 was closed by mechanism rather than by
#: measurement. On the upgraded plan **every** slug is accepted, so the pin is real at last; it is
#: passed through `KEEL_COPILOT_MODEL`, keel-runtime's own way in, because the skill passes no
#: `--copilot-model` and a founder passes nothing at all.
#:
#: **Why this slug and not the router's own default.** The plan's default is now `claude-sonnet-5`,
#: and on that model **every keel-runtime job fails** (`runs/DRIFT.md` **#59**): Copilot's
#: Anthropic-vendored `assistant.message` events carry no `phase` key, and
#: `executor._copilot_final_answer` reads only the `final_answer`-phase message, so a correct
#: answer in the right shape is thrown away and the job is reported failed with `exit_code: 0` and
#: no error anywhere. That run stands in `runs/` as the evidence, red, and nothing here is
#: asserted more loosely because of it.
#:
#: `gpt-5.6-luna` emits `phase` (measured, same CLI, same flags, one variable) **and** is the model
#: the router happened to choose for all 129 answered cases of
#: `runs/20260909T061537Z-instructions-copilot` -- so pinning it is also what makes this run and
#: that one the same measurement rather than two. C-5's own words: *`auto` is never used in a
#: measured run.*
RUNTIME_MODEL = "gpt-5.6-luna"

#: **What the runtime pins, per host -- and one of the two is deliberately nothing.**
#: keel-runtime's `ClaudeCodeExecutor._build_argv` never passes a model and there is no
#: `KEEL_CLAUDE_MODEL` to set, so a Claude journey's runtime model is **recorded, not pinned**:
#: read back off the per-job envelopes the CLI itself writes. Inventing a pin that the runtime
#: ignores would put a fact about the referee into the bundle.
#:
#: **And on the Keel door there is no runtime at all**, so there is nothing to pin and nobody to
#: pin it: keel-cloud chooses the model per screen class from its own routing table and reports
#: what answered in `execution.model_used` (keel-cloud spec 045 FR-016/FR-018/FR-043), which this
#: run records and asserts nothing about.
RUNTIME_MODEL_FOR_HOST = {"copilot": RUNTIME_MODEL, "claude": None, "codex": None, "keel": None}

#: **The host's model is a different question, and gets the founder's own answer.** Leg one asks
#: what happens when the founder types "keel connect" into *their* CLI, so it pins what their CLI
#: would have chosen anyway -- Copilot CLI 1.0.83 on the upgraded plan logs *"Using default model:
#: claude-sonnet-5"*, and Claude Code's default is whatever that account is configured for, which
#: this run records rather than overrides. Pinning keeps the run reproducible without making it
#: unrepresentative; putting the runtime's slug here instead would have measured a founder nobody
#: is. On Copilot the two pins disagree because #59 made them disagree, and the bundle records
#: both and why.
HOST_MODEL_FOR_HOST = {"copilot": "claude-sonnet-5", "claude": None, "codex": None, "keel": None}
#: keel-runtime's per-host pin variable (spec 005 C-5 for Copilot, spec 008 for Codex); Claude's
#: executor takes none. Read here so a cell's environment can pin the runtime's model.
RUNTIME_MODEL_ENV_FOR_HOST = {"copilot": "KEEL_COPILOT_MODEL", "codex": "KEEL_CODEX_MODEL"}

#: The Copilot-era name for the host pin's override, kept because a run record names it.
HOST_MODEL_ENV = ("KEEL_JOURNEY_HOST_MODEL", "KEEL_S012_HOST_MODEL")

#: The founder's own three, in the order the guided walk takes them.
STAGES = ("PROBLEM", "SOLUTION", "COMMERCIAL")

#: What the runtime's own startup line must say before leg two spends anything (FR-006).
EXPECTED_EXECUTOR = agent_host.EXECUTOR_FOR_HOST[HOST]

#: keel-cloud's own terminal-failure statuses, borrowed from `harness/refusals.py` so the two
#: readings of "refused" cannot drift apart.
REFUSED = refusals.TERMINAL_FAILURE_STATUSES

#: The statuses an interaction is allowed to end this journey in. `APPLIED` is a stage that landed;
#: `ACCEPTED` is a frame whose own chained child did the applying; `AWAITING_CONFIRMATION` is a card
#: sitting on the screen waiting for the founder, which is where the last one legitimately is.
SETTLED = frozenset({"APPLIED", "ACCEPTED", "AWAITING_CONFIRMATION"})

#: Bounded, benign, and never an attack: what the founder says when a live model answers a claim
#: box with a question instead of a card. Spec 008's own allowance -- *a question is an answer, and
#: the walk goes on* -- with S-004's ceiling of three, so a model that will not land a claim costs
#: a known number of premium requests rather than an open-ended one.
FOLLOW_UPS = [
    "That is the whole of it. Please write up what you have understood.",
    "Nothing else to add -- go ahead and write up the claim from what I have said.",
    "I have no more detail. Write up what you have understood so far.",
]


def _now() -> float:
    return time.monotonic()


class KeelsAiRefused(AssertionError):
    """**The door is shut, and keel-cloud said so by name** (spec 024 FR-010; keel-cloud spec 045
    FR-032, FR-037, FR-039, FR-009).

    An `AssertionError` rather than a bare exception because that is what it is: the journey's
    first requirement of this door is that the door opens, and it did not. It carries keel-cloud's
    own words and is raised **where the wire said them**, not five minutes later on a screen that
    never changed.
    """


def _named_failure(get_json, project_id: str) -> dict | None:
    """The first job of this project that failed for one of Keel's-AI four named reasons, or
    `None`.

    Read off the founder-gated list -- the same document `harness/refusals.py::latest_failure`
    reads -- because the reason travels in the job's `error_message` and **not** in its
    `error.code` (keel-cloud spec 045 Assumption 11: the five wire codes are not extended, because
    a sixth would be a founder-visible vocabulary change keel-web has no spec for). So the code
    beside it is one of the five ordinary ones -- `LLM_UNAVAILABLE` for a disabled executor and for
    the daily cap, `EXECUTOR_TIMEOUT` for the job clock, `INTERNAL_ERROR` for a restart sweep --
    and the name is in the message.
    """
    rows = get_json(f"/v2/inference-interactions?project_id={project_id}")
    if not isinstance(rows, list):
        return None
    for row in rows:
        job = row.get("job") or {}
        error = job.get("error") or {}
        message = error.get("message") or job.get("error_message") or ""
        reason = keels_ai.named_reason(message)
        if reason:
            return {"reason": reason, "why": keels_ai.NAMED_REASONS[reason],
                    "screen": row.get("screen"), "interaction_id": row.get("interaction_id"),
                    "job_id": job.get("job_id"), "job_status": job.get("status"),
                    "error_code": error.get("code"), "error_message": message}
    return None


def _refuse_if_the_door_is_shut(recorder, get_json, project_id: str) -> None:
    """Raise `KeelsAiRefused`, in a step of its own, the moment the wire names one of the four.

    The step is what makes the verdict readable: `recorder.failed_step` takes the **first** failed
    step's name, so a bundle whose executor was switched off says `KEEL_AI_DISABLED` in
    `verdict.json` and in the matrix's own summary row -- which is the difference between a
    founder reading *the key is missing on the twin* and a founder reading *something timed out*.
    """
    found = _named_failure(get_json, project_id)
    if found is None:
        return
    with recorder.step(f"spec 024 FR-010: Keel's AI could not run this job -- {found['reason']}",
                        party="stack", kind="assert") as h:
        h.record_assert({"a job that ran": True}, found)
        raise KeelsAiRefused(
            f"Keel's AI refused this journey at {found['screen']}: {found['error_code']} / "
            f"{found['error_message']} -- {found['why']}. Nothing here waited for a timeout; "
            f"keel-cloud named the reason and this is it.")


def _wait_for_turn(chat, recorder, get_json, project_id: str, *, timeout_s: float) -> dict:
    """`Chat.wait_for_agent_turn`, and on the Keel door **a question to the wire every thirty
    seconds while it waits** (spec 024 FR-010).

    The three CLI hosts take the branch they have always taken -- one call, one wait, byte for
    byte what spec 016 wrote -- because on those hosts a job that fails leaves a `runs/DRIFT.md`
    #37-shaped silence that the existing `except TimeoutError` already interrogates, and nothing
    about them fails *before a socket is opened*.

    Keel's AI does. `KEEL_AI_DISABLED` and `KEEL_AI_DAILY_CAP` are answered in under a second and
    the screen simply never changes, so the ceiling is split into chunks and the wire is asked
    between them. The total wait is the same total wait; what changes is how long a door that was
    never going to open takes to say so.
    """
    if not KEELS_AI:
        return chat.wait_for_agent_turn(timeout_s=timeout_s)
    deadline = _now() + timeout_s
    while True:
        remaining = deadline - _now()
        if remaining <= 0:
            raise TimeoutError(
                f"no agent turn within {timeout_s}s, and the wire named none of "
                f"{sorted(keels_ai.NAMED_REASONS)}")
        try:
            return chat.wait_for_agent_turn(timeout_s=min(NAMED_REASON_POLL_S, remaining))
        except TimeoutError:
            _refuse_if_the_door_is_shut(recorder, get_json, project_id)


def _wait_for_review_card(chat, recorder, get_json, project_id: str, stage: str, *,
                           timeout_s: float) -> dict:
    """`Chat.wait_for_review`, chunked exactly as `_wait_for_turn` chunks the agent-turn wait, and
    for the same reason (spec 024 FR-010). The card this waits for is the *chained* job's -- the
    assumptions job `save_confirmation` starts -- so the same four named reasons can fail it after
    the claim was already saved and the screen simply stops moving: a flat page-poll would sit out
    the whole `timeout_s` ceiling before saying so, on a job the wire already knows was refunded.

    Only the Keel door chunks; the three CLI hosts take the one call they have always taken.
    """
    if not KEELS_AI:
        return chat.wait_for_review(project_id, stage, timeout_s=timeout_s)
    deadline = _now() + timeout_s
    while True:
        remaining = deadline - _now()
        if remaining <= 0:
            raise TimeoutError(
                f"the {stage} review card never rendered within {timeout_s}s of saving the "
                f"confirmed claim, and the wire named none of {sorted(keels_ai.NAMED_REASONS)}")
        try:
            return chat.wait_for_review(project_id, stage,
                                         timeout_s=min(NAMED_REASON_POLL_S, remaining))
        except TimeoutError:
            _refuse_if_the_door_is_shut(recorder, get_json, project_id)


def _land_the_card(page, recorder, get_json, project_id, stage, opening, *, timeout_s=300.0):
    """**The first model job of a stage**: the founder says their statement, the host's model
    thinks, and a confirmation card carrying a non-empty claim comes back.

    Split out of `_walk_stage_live` for spec 021 and for nothing else: the short journey ends here,
    on the PROBLEM stage, and the full journey goes straight on from here into the review. Both
    call this; neither has a copy of it. The assertion the short run makes is therefore *literally*
    the assertion the full run makes at the same point, rather than a second one written to look
    like it.
    """
    chat = Chat(page, recorder)
    chat.send(opening)
    turn = _agent_answers(chat, recorder, get_json, project_id, stage, timeout_s=timeout_s)
    card = chat.confirmation_card()
    stops: list[dict] = []

    for round_no, benign in enumerate(FOLLOW_UPS, start=1):
        if card is not None:
            break
        # Spec 024 FR-010, before a single follow-up is typed: the three benign sentences exist
        # because a *live model* sometimes answers a claim box with a question and a founder would
        # say more. They are the wrong answer to a door with no key behind it, where each one
        # spends another framing's worth of credits arriving at the same sentence.
        if KEELS_AI:
            _refuse_if_the_door_is_shut(recorder, get_json, project_id)
        stopped = (turn or {}).get("stopped")
        if stopped:
            stops.append(stopped)
        why = ("its job failed" if stopped else "it came back with a question")
        with recorder.step(f"§1.1: {stage} produced no card because {why}, so the founder says "
                            f"more ({round_no} of {len(FOLLOW_UPS)})",
                            party="founder", kind="note") as h:
            h.record_wire({"benign": benign},
                           {"the wire": stopped,
                            "reply": (turn or {}).get("agent_reply", "")[:2000]})
        chat.send(benign)
        turn = _agent_answers(chat, recorder, get_json, project_id, stage, timeout_s=timeout_s)
        card = chat.confirmation_card()
    if (turn or {}).get("stopped"):
        stops.append(turn["stopped"])

    with recorder.step(f"§1.1: {stage} comes back as a confirmation card the host's model wrote",
                        party="founder", kind="assert") as h:
        h.record_assert({"a card": "with a non-empty claim", "stops": []},
                         {"card": card, "what stopped it, in keel-cloud's own words": stops})
        assert card is not None, (
            f"{HOST} never landed a confirmation card on {stage} after {len(FOLLOW_UPS)} "
            f"benign follow-ups"
            + ("; the wire says: " + " | ".join(refusals.describe(s) for s in stops)
               if stops else ", and the wire had nothing to add"))
        assert (card.get("claim") or "").strip(), f"the {stage} card carries no claim: {card!r}"
    if stops:
        # A stage that landed only after a job of its own had failed is still a green stage --
        # and it is also a fact about this host that the bundle must not lose.
        with recorder.step(f"§1.1: {stage} landed, but not on the first try",
                            party="stack", kind="note") as h:
            h.record_wire(None, {"jobs that failed before the card": stops})
    return chat, card


def _read_the_lines(page, recorder, get_json, project_id, stage, chat, *, timeout_s=300.0):
    """**The stage's second model job, and what it produced**: the founder saves the confirmation
    card, keel-cloud chains the frame's own `<STAGE>_ASSUMPTIONS` off it with nothing pressed, and
    the review card lands carrying numbered lines and a separated deal-breaker.

    **It does not carry pick lists, and since keel-cloud spec 048 it cannot** -- the questionnaire
    is the project's, written by one `QUESTIONS` call after the last framed stage is approved, which
    is after every card this reads. The assertion that every line offers a pick list has moved to
    `_the_questions_land`; the long comment at the step below says why, and spec 026 FR-002 is the
    requirement.

    Split out of `_walk_stage_live` for the same reason `_land_the_card` was split out of it (spec
    021), and for one more: the **short Keel's-AI cell** stops here (spec 024, the founder,
    2026-09-29 -- *"only the framing-and-assumptions part, at different effort settings, to keep
    spend down"*). So the assertions that cell makes about the lines are *literally* the
    assertions the full journey makes at the same point, called from the same function, rather
    than a copy of them that would have to be kept in step.

    Returns the `ReviewCard` page object, un-approved: whether to approve it is the caller's, and
    it is the one thing the short run does not do.
    """
    chat.save_confirmation()
    review_timeout_s = KEELS_AI_JOB_WAIT_S if KEELS_AI else timeout_s + 180
    landed = _wait_for_review_card(chat, recorder, get_json, project_id, stage,
                                    timeout_s=review_timeout_s)
    with recorder.step(f"§1.2: the {stage} review opened itself, with no button pressed",
                        party="founder", kind="assert") as h:
        h.record_assert({"the review opened": True}, landed)

    card_page = ReviewCard(page, recorder, _web_base_of(page))
    opened = card_page.open(project_id, stage)
    with recorder.step(f"§1.2: the {stage} card reads Reviewing", party="founder",
                        kind="assert") as h:
        h.record_assert("Reviewing", opened["status"])
        assert "review" in opened["status"].lower(), (
            f"expected Reviewing on {stage}, got {opened['status']!r}")

    # FR-007: shapes, never content.
    with recorder.step(f"§1.2: the {stage} card carries numbered lines and separates at least one "
                        "deal-breaker", party="founder", kind="assert") as h:
        lines = card_page.lines()
        rule_lines = card_page.rule_lines()
        # **The chips are recorded here and asserted below, after the questions land** (spec 026
        # FR-002/FR-003; keel-cloud spec 048; keel-web spec 026 FR-012).
        #
        # Until 048 a stage *could not be approved without its own questionnaire* --
        # `ScreenResultApplier.confirmCommand` ran `frame -> introduceRoles ->
        # introduceAssumptions -> approve` in one apply and `introduceAssumptions` took a
        # questionnaire -- so *the lines are approved* and *the questions exist* were one event and
        # every review card a founder ever read had pick lists under its lines. This step asserted
        # that, correctly, for as long as it was true:
        #
        #     assert all(line.get("chips") for line in lines)
        #
        # 048 splits that moment in two. `introduceAssumptions` takes beliefs, roles and
        # rationales; the questionnaire is the **project's** and is written by **one `QUESTIONS`
        # call** that runs when the last framed stage is approved -- strictly after every card this
        # function reads. keel-web 026 FR-012 draws the consequence in markup: `ReviewLine` renders
        # `{selection ? <Chips …/> : null}`, and a card on which no line resolves a control says so
        # **once**, in `QUESTIONS_NOT_WRITTEN_YET`, rather than drawing empty pick lists. Matrix run
        # 36862514753 on staging 782a01a -- the first run on the new build -- went red here in under
        # two minutes, on the first card of three, for asserting a screen shows something the
        # product is designed not to show it.
        #
        # **The assertion is moved, not dropped**: `_the_questions_land` below makes it against the
        # project's one questionnaire (every selection offers a pick list) and against the slice
        # each approved card carries. And the **absence** of chips is not asserted either, because
        # it is not reliably true: a `SOLUTION` or `COMMERCIAL` line that `reads` an earlier stage's
        # measurement is given the referent's own `selectionId` (keel-cloud 049 FR-013), so it owns
        # a control the earlier approval already wrote and draws chips on an unapproved card. That
        # is 049 working, and a run that refused it would be refusing the feature.
        chipped = [line.get("heading") for line in lines if line.get("chips")]
        h.record_assert({"lines": ">= 1, each numbered", "rule lines": "one names deal-breakers"},
                         {"lines": len(lines), "rule lines": rule_lines,
                          "headings": [line.get("heading") for line in lines],
                          "first line": (lines[0] if lines else None),
                          "lines carrying a pick list already (keel-cloud 049: a line that reads "
                          "an earlier stage's measurement owns that stage's control), recorded "
                          "and asserted nowhere": chipped})
        assert lines, f"the {stage} card rendered no lines at all"
        unnumbered = [line.get("heading") for line in lines
                      if not str(line.get("number") or "").strip()]
        assert not unnumbered, f"a {stage} line is unnumbered: {unnumbered}"
        assert any("deal-breaker" in line.lower() for line in rule_lines), (
            f"the {stage} card separates no deal-breaker from what is worth knowing: "
            f"{rule_lines!r}")
    return card_page


def _walk_stage_live(page, recorder, get_json, project_id, stage, opening, *, timeout_s=300.0):
    """One stage of the guided walk, against a **live** model.

    Deliberately not `evals/preludes.py::walk_stage`. That one asserts the confirmation card's
    claim **verbatim** against the generated script, which is exactly right for a scripted executor
    and meaningless against a model that writes its own sentence; and its 90-second waits are a
    scripted runtime's, not a live one's. Copying it here rather than growing a `live=` branch on
    it is the choice spec 016's plan states: `walk_stage` is six deterministic scenarios' contract
    with the corpus, and a conditional in it would make all six read like this one.
    """
    chat, _card = _land_the_card(page, recorder, get_json, project_id, stage, opening,
                                 timeout_s=timeout_s)
    card_page = _read_the_lines(page, recorder, get_json, project_id, stage, chat,
                                timeout_s=timeout_s)
    card_page.approve()
    with recorder.step(f"§1.2 wire: {stage} is framed and approved after approval, and nothing on "
                        "the chain was refused", party="stack", kind="assert") as h:
        overview_body = get_json(f"/v2/projects/{project_id}/overview") or {}
        after = next((s for s in overview_body.get("stages") or [] if s.get("type") == stage), {})
        refusal = refusals.stage_refusal(get_json, project_id, stage)
        h.record_assert({"framed": True, "approved": True, "refusal": None},
                         {**after, "refusal": refusal})
        assert refusal is None, f"{stage} was refused: {refusals.describe(refusal)}"
        assert after.get("framed") is True and after.get("approved") is True, (
            f"expected {stage} framed+approved, got {after}")
    return card_page


def _beliefs_on(card: dict) -> list[dict]:
    """Every belief a stage card carries, both buckets, in render order.

    `StageCard.groups[] -> {roleLabel, loadBearing[], supporting[]}` is the wire's own shape
    (`canon/openapi-v2.yaml`), and both halves point at controls: the split is *what happens if this
    is wrong*, not *is this asked*.
    """
    out: list[dict] = []
    for group in card.get("groups") or []:
        out.extend(group.get("loadBearing") or [])
        out.extend(group.get("supporting") or [])
    return out


# ------------------------------------------------------- the deck's own three readings, derived
# **These three are the wire's own arithmetic, restated here so the deck can be compared against
# it** (spec 027 §1.7). Each one is keel-web's own helper, read at keel-web master `7e5a2a8` and
# written out in Python: `measuredStatus`+`washOf` (`src/lib/translate.ts`,
# `src/components/brief/ShipFigure.tsx`), `linesOfStage` and `worstStage`
# (`src/components/brief/lines.ts`).
#
# Restating them is the opposite of recomputing a verdict. Every input is a field `GET
# /v2/projects/{id}/overview` or `GET /v2/projects/{id}/standing` sent; nothing here decides a
# verdict, a median or a standing, and if keel-cloud's own numbers moved these would move with
# them. What they let the referee say is *the screen's number is the wire's number*, which is the
# one thing a screen can get wrong on its own.

#: `Verdict` -> the band and panel modifier keel-web paints it with. `measuredStatus` answers tone
#: `good`/`bad`/`warn` for the three verdicts and `mute` for everything else, and `washOf` collapses
#: anything that is not one of the first three to `none` -- so an absent verdict and an `UNTESTED`
#: one are the same wash, which is what *no evidence* has always meant on a `.bar`.
_WASH_OF_VERDICT = {"SUPPORTED": "good", "CONTRADICTED": "bad", "MIXED": "warn"}

#: Worst first (keel-web `WORST_FIRST`): a deal-breaker that failed is worse than one people split
#: on, and **`UNTESTED` before `SUPPORTED`**, because *nothing known* is a worse place to be than
#: *holding up*.
_WORST_FIRST = ("CONTRADICTED", "MIXED", "UNTESTED", "SUPPORTED")


def _band_wash(summary: dict) -> str:
    """The `band--*`/`panel--*` modifier this stage's own verdict implies."""
    return _WASH_OF_VERDICT.get((summary.get("verdict") or "").upper(), "none")


def _stage_lines(standing: dict, stage: str) -> dict:
    """`GET /v2/projects/{id}/standing`'s four lists filtered to one stage, with the two numbers
    the panel's count line is made of: `total` over all four, `holding` from `holdingUp` alone."""
    def of(key: str) -> list:
        return [line for line in (standing.get(key) or []) if line.get("stage") == stage]
    up, down, split, none = (of("holdingUp"), of("notHoldingUp"),
                             of("peopleDisagree"), of("untested"))
    return {"holdingUp": len(up), "notHoldingUp": len(down), "peopleDisagree": len(split),
            "untested": len(none), "holding": len(up),
            "total": len(up) + len(down) + len(split) + len(none)}


def _tested_lines(counted: dict) -> int:
    """How many of a stage's lines the five answers actually **tested**: `holdingUp` +
    `notHoldingUp` + `peopleDisagree`, from `GET /standing`'s own lists.

    `untested` is deliberately not in it. A panel has two parts, *Held* and *Did not hold*, and no
    third one (keel-web spec 027 FR-008…FR-012), so an untested line has nowhere on a panel to be
    and a stage whose every line is untested draws nothing -- correctly. The assertion that read
    *lines on the wire and no rows on the panel* as a fault blamed keel-web for obeying its own
    spec, and spent matrix run 36895521843 doing it (spec 028 FR-018/FR-019).
    """
    return counted["holdingUp"] + counted["notHoldingUp"] + counted["peopleDisagree"]


def _tail_number(tail: str | None) -> int:
    """The *N* in a part's tail, *2 more ›* -- `0` where the part is open.

    **A budget moves a number; it never deletes one** (keel-web FR-015). A part closed at the
    rest-of-three limit shows three rows and a tail standing for the rest, so counting only the
    rows would under-count every closed part and opening the tails first would break *the worst
    stage's panel is the one open at rest* three steps below, which reads exactly those tails.
    """
    if not tail:
        return 0
    found = re.search(r"\d+", tail)
    return int(found.group()) if found else 0


def _panel_accounting(panel: dict | None, counted: dict) -> dict:
    """What this panel accounts for, against what the wire says it should: one sum against one sum.

    **2026-10-03: no subject on the board, and kept for the reason the thing it counted was kept**
    (keel-web **038** FR-009/FR-013). A card is a snapshot of deal-breakers: it has no *Held* list,
    no worth-knowing line and no line past the second failing deal-breaker, so there is no sum on
    the screen to put against `GET /standing`'s. What stands in its place is
    `_expected_card()` -- the state rule, the cap and the tail at its own number -- and the
    whole-project line count, which moved to the ship column's own tile (FR-003) and is asserted
    there. This function, `_tested_lines` and `_tail_number` keep their last callers in
    `tests/test_journey_untested_stage.py`, which is the record of what run 36895521843 cost; a
    reader is retired when the thing it reads is.

    `{tested, held, did not hold, tails, accounted}`. Every number is counted, never computed: the
    four on the left are rows and tails on the screen, the one on the right is a length of a list
    the wire sent.
    """
    held = Overview.lines_of(panel or {}, Overview.PANEL_HELD)
    failed = Overview.lines_of(panel or {}, Overview.PANEL_DID_NOT_HOLD)
    tails = [_tail_number(Overview.tail_of(panel or {}, Overview.PANEL_HELD)),
             _tail_number(Overview.tail_of(panel or {}, Overview.PANEL_DID_NOT_HOLD))]
    return {"tested on the wire": _tested_lines(counted),
            "HELD rows shown": len(held), "DID NOT HOLD rows shown": len(failed),
            "the tails' own numbers": tails,
            "rows the panel accounts for": len(held) + len(failed) + sum(tails)}


#: What `GET /stages/{stage}` says about **how the answers were read**, summed over the stage's own
#: beliefs. `anchored` is `inside + outside` -- the answers that counted, either way; `guessed` is
#: keel-cloud's own *"answers shown to the founder that count towards nothing"*; `escaped` is
#: *"answers that recorded nothing at all -- an escape, or a blank occasion"*. These three are the
#: only place on the wire that can tell a lying referee from a broken product (spec 028 FR-021).
ANCHORING_KEYS = ("anchored", "guessed", "escaped")


def _stage_anchoring(card: dict) -> dict:
    """One approved card's `BeliefStanding` counts, summed over every belief it carries."""
    out = {key: 0 for key in ANCHORING_KEYS}
    out["lines"] = 0
    for group in (card or {}).get("groups") or []:
        for belief in (group.get("loadBearing") or []) + (group.get("supporting") or []):
            standing = belief.get("standing") or {}
            out["lines"] += 1
            out["anchored"] += (standing.get("inside") or 0) + (standing.get("outside") or 0)
            out["guessed"] += standing.get("guessed") or 0
            out["escaped"] += standing.get("escaped") or 0
    return out


def _whose_fault(anchoring: dict) -> str:
    """Who to look at when an approved stage is entirely untested and everybody answered.

    **Anchored nothing and guessed something is the stranger's**: the answers reached keel-cloud,
    were shown to the founder, and counted towards nothing -- which is what the wire says about a
    sentence that is not an occasion. That is this repository's bug and spec 028 is the fix for the
    one shape of it that has happened. Anything else is keel-cloud's: answers that were read as
    occasions and counted, on a stage that still has nothing standing, is a product finding.
    """
    if anchoring["anchored"] == 0 and anchoring["guessed"] > 0:
        return ("THE STRANGER'S -- this harness typed something keel-cloud read as a guess, not "
                "an occasion. A guess is shown to the founder and counts towards nothing "
                "(`BeliefStanding.guessed`), so the picks underneath it were stored and tested "
                "nothing. Read §2.3's own per-anchor record: whichever anchor's `path` is "
                "*composed from their own facts* is where to look first (spec 028)")
    if anchoring["anchored"] == 0 and anchoring["escaped"] > 0:
        return ("THE STRANGER'S -- every answer on this stage's occasion was an escape. An escape "
                "is an honest answer and it tests nothing, so a stage asked only of people who "
                "escaped it is a stage nobody answered")
    return ("KEEL-CLOUD'S -- the answers were read as occasions and counted "
            f"(anchored {anchoring['anchored']}) and the stage still has nothing standing. That "
            "is a product finding, and the first this scenario has been able to make: a "
            "`runs/DRIFT.md` entry, never a workaround here (AGENTS.md)")


# --------------------------------------------- the board's own rule, restated (keel-web spec 038)
# **The same discipline as the three above, for the four regions keel-web `038-overview-board`
# (merged `4540aa3`, 2026-10-01; keel-cloud `canon/designs/overview-board-design.md` §4) put in
# their place.** Every input below is a field `GET /overview` or `GET /standing` sent; nothing here
# decides a verdict, a median or a standing. What they let the referee say is *the card is in the
# state the wire's own numbers put it in, and its rows are the wire's own rows* -- which is the one
# thing a card can get wrong on its own.

#: `measuredStatus`'s tone, **unwashed** -- `mute` where `washOf` would say `none`. The pill and
#: the band wear the washed one (`_WASH_OF_VERDICT`); the headline word wears this one, because
#: `OverviewRoute` writes `st-${headline.tone}` straight off `measuredStatus` (FR-001).
_TONE_OF_VERDICT = {"SUPPORTED": "good", "CONTRADICTED": "bad", "MIXED": "warn"}

#: The verdict rule's own floor, as `translate.ts`'s `VERDICT_PEOPLE_FLOOR` spells it. State C's row
#: is `panelAnsweredOfFloor` -- *3 people answered · 5 needed* -- and design open question 4's
#: offer of a `peopleNeeded` wire field is the one the founder declined, so there is nothing on the
#: wire to read it off and this is the number the screen must say.
VERDICT_PEOPLE_FLOOR = 5


def _status_tone(summary: dict) -> str:
    """The tone `measuredStatus` gives this stage's own verdict, unwashed."""
    return _TONE_OF_VERDICT.get((summary.get("verdict") or "").upper(), "mute")


def _stage_deal_breakers(standing: dict, stage: str) -> list[dict]:
    """**State B's own rows, taken from the wire** (keel-web 038 FR-010): `notHoldingUp ∩ stage ∩
    LOAD_BEARING` **then** `peopleDisagree ∩ stage ∩ LOAD_BEARING`, each in `GET /standing`'s own
    order -- so the first two are the two worst, which is the whole of the cap's own argument (P5).

    `{heading, tone, assumptionId}`: `heading` is `beliefHeading` -- `heading`, falling back to
    `statement` -- and `tone` is the glyph the row must carry, `bad` for a `CONTRADICTED`
    deal-breaker and `warn` for a `MIXED` one. The glyph is the **only** carrier left of which of
    the two a row is, now that the risk tag and the landed clause have gone (design §5.7).
    """
    def of(key: str, tone: str) -> list[dict]:
        return [{"heading": " ".join(((line.get("heading") or line.get("statement") or "")
                                      ).split()),
                 "tone": tone, "assumptionId": line.get("assumptionId")}
                for line in (standing.get(key) or [])
                if line.get("stage") == stage
                and (line.get("risk") or "").upper() == "LOAD_BEARING"]
    return of("notHoldingUp", "bad") + of("peopleDisagree", "warn")


def _expected_card(summary: dict, failed: list[dict]) -> dict:
    """**What keel-web 038's own rule makes this stage's card**, from the wire alone.

    The three states are exhaustive and disjoint and the order *is* the rule (FR-009, design
    §4.3): **C** where the verdict is `UNTESTED` or absent, **A** where
    `dealBreakersHolding === dealBreakersTotal`, **B** otherwise. From that follow the body's own
    numbers -- how many rows, whether there is a tail and at what number, and whether the foot is
    drawn at all.

    **The one edge case** (FR-012, design §4.3): `dealBreakersTotal === 0` satisfies state A's
    condition and *No major blockers* would be true but hollow, so the card draws **no row** and
    shows the foot's *N people answered* alone.
    """
    verdict = (summary.get("verdict") or "").upper()
    total = summary.get("dealBreakersTotal") or 0
    holding = summary.get("dealBreakersHolding") or 0
    if verdict not in _WASH_OF_VERDICT:
        state = "C"
    elif holding == total:
        state = "A"
    else:
        state = "B"
    over = max(len(failed) - Overview.ROW_CAP, 0)
    if state == "B":
        rows = min(len(failed), Overview.ROW_CAP)
    elif state == "A":
        rows = 1 if total else 0
    else:
        rows = 1
    return {"state": state,
            "rows": rows,
            "tail": over if state == "B" and over else 0,
            "foot": state != "C",
            "deal-breakers, on the wire": [holding, total],
            "peopleAnswered": summary.get("peopleAnswered"),
            "every failing deal-breaker the wire carries": [row["heading"] for row in failed],
            "the two the cap shows": [row["heading"] for row in failed[:Overview.ROW_CAP]]
                                     if state == "B" else [],
            "their own glyphs": [row["tone"] for row in failed[:Overview.ROW_CAP]]
                                if state == "B" else []}


def _worst_stage(by_stage: dict) -> str:
    """The stage keel-web opens at rest: the worst verdict the wire sent, a tie going to the
    **deepest band** -- which is `STAGES` order, problem first, on the design's own argument that
    the keel is the part whose failure capsizes the rest."""
    def rank(stage: str) -> int:
        verdict = ((by_stage.get(stage) or {}).get("verdict") or "UNTESTED").upper()
        return _WORST_FIRST.index(verdict) if verdict in _WORST_FIRST \
            else _WORST_FIRST.index("UNTESTED")
    return min(STAGES, key=rank)


def _the_questions_land(page, recorder, get_json, post_json, project_id, *, timeout_s=None):
    """**The project's one questionnaire, waited for where keel-cloud actually writes it** (spec
    `026-journey-one-questionnaire` FR-004 to FR-014; keel-cloud specs 048 and 049; keel-web spec
    026).

    Until 048 this step could not have existed, because the moment it waits for did not: a stage
    could not be approved without its own questionnaire, so *the lines are approved* and *the
    questions exist* were one event. 048 splits them. `introduceAssumptions` takes beliefs, roles
    and rationales; `writeQuestionnaire` is its own command, applied by **one `QUESTIONS` call**
    that keel-cloud starts when `allFramedStagesApproved()` becomes true and that sees every settled
    belief on the project. The founder is left looking at three approved cards and a People entry
    that is still locked -- which is what `Overview.questionsState` exists to say, in four words:
    `NOT_STARTED`, `WRITING`, `READY`, `FAILED`.

    **Waited for once, after the third approval, and not after each one.** A `QUESTIONS` call runs
    after *every* approval in this walk -- an unframed stage is skipped rather than waited on
    (`journeys.md` §1.2) -- so the first two write questionnaires that are rewritten whole before
    anybody is ever shown them. The one that matters is the one standing after the last approval,
    and the place the founder waits for it is the place their next click is: People.

    **Four assertions, in the order the evidence arrives.**

    1. the state reaches `READY` inside the ceiling, with one retry spent on a `FAILED`;
    2. the questionnaire itself -- anchors with prompts, **every selection offering a pick list**
       (this is the assertion `_read_the_lines` used to make against a review card's chips), and
       ids that are the project's rather than a stage's;
    3. each stage card's **slice**: every `selectionId` its beliefs name resolves against that one
       questionnaire, and every `readsBelief` points at a stage and a line that exist;
    4. the same thing on the screen, because a slice that reached a JSON reader and not a founder
       is not the feature.

    Nothing here reads a word the model wrote (spec 016 FR-007): the prompts, the option labels and
    the card's own sentences are its own, and what is asserted is presence, resolution and count.
    """
    ceiling = QUESTIONS_WAIT_S if timeout_s is None else timeout_s
    screen = corpus_script.QUESTIONS_SCREEN
    retry_path = f"/v2/projects/{project_id}/questionnaire/retry"
    started = _now()
    deadline = started + ceiling
    seen: list[str | None] = []
    state: str | None = None
    retried: dict | None = None
    retried_the_attempt: str | None = None

    while _now() < deadline:
        state = (get_json(f"/v2/projects/{project_id}/overview") or {}).get("questionsState")
        if not seen or seen[-1] != state:
            seen.append(state)
        if state == "READY":
            break
        if state == "FAILED":
            # keel-cloud's own words for what went wrong, read off the screen that has no stage
            # (`InferenceScreen.QUESTIONS` carries none -- the questionnaire is the project's), so
            # `latest_failure`'s stage key cannot find it.
            failure = refusals.latest_failure_on_screen(get_json, project_id, screen)
            this_attempt = (failure or {}).get("interaction_id")
            if retried is None:
                # FR-006, and it is the founder's own button: keel-web spec 026 FR-019 offers *Try
                # again* beside the locked People entry and nowhere else, and keel-cloud refuses
                # the endpoint in every state but `FAILED` (422, rule `screen`) -- so the only
                # state it is sent in is the only state it is legal in. Once, and only once.
                with recorder.step("§1.3: the QUESTIONS call gave up, so the founder presses *Try "
                                    "again* -- once", party="founder", kind="note") as h:
                    retried = post_json(retry_path)
                    retried_the_attempt = this_attempt
                    h.record_wire({"the founder's one control": "Try again"},
                                   {"answer": retried, "what keel-cloud said went wrong": failure})
            elif this_attempt and this_attempt != retried_the_attempt:
                # The retry failed too. Stop here rather than sitting out the ceiling: the wire has
                # said everything it is going to say.
                break
        if KEELS_AI:
            # Spec 024 FR-010, on every poll rather than after the deadline: `KEEL_AI_DISABLED` and
            # `KEEL_AI_DAILY_CAP` are answered before a socket is opened, so a run that waited the
            # whole ceiling for one would be reporting the referee's patience, not the product's
            # sentence.
            _refuse_if_the_door_is_shut(recorder, get_json, project_id)
        page.wait_for_timeout(3_000)

    waited = _now() - started
    with recorder.step("§1.3: keel-cloud wrote the project's one questionnaire, and the overview "
                        "says so", party="stack", kind="assert") as h:
        failure = refusals.latest_failure_on_screen(get_json, project_id, screen)
        h.record_assert({"questionsState": "READY"},
                         {"questionsState": state, "the states it went through, in order": seen,
                          "the founder waited, in seconds": round(waited, 1),
                          "the ceiling, in seconds": ceiling,
                          "the retry, where one was spent": retried,
                          "what keel-cloud said went wrong": failure,
                          "whose clock the ceiling is": (
                              "keel-cloud's QUESTIONS abandonment plus queue and poll slack; the "
                              "Keel door's own 600s abandonment where this is that door")})
        assert state is not None, (
            "the overview answered no `questionsState` at all. keel-cloud spec 048 FR-039 puts it "
            "there, so a build without it is older than 048 -- which means this journey is being "
            "run against a deployment that still writes a questionnaire per stage, and the rest of "
            "these assertions would be measuring something else. (keel-web falls back to "
            "`stages.every(approved)` for exactly that case; the referee does not, because the "
            "fallback would hide the finding.)")
        assert state == "READY", (
            f"the project's questionnaire never became READY within {ceiling:.0f}s -- it went "
            f"{seen} and stopped at {state!r}"
            + (f". keel-cloud says: {refusals.describe(failure)}" if failure else
               ". The wire named nothing: a NOT_STARTED at the deadline means the approval started "
               "no QUESTIONS job at all, and a WRITING means one is still running.")
            + (f" One retry was spent: {retried}." if retried else ""))

    questionnaire = get_json(f"/v2/projects/{project_id}/questionnaire") or {}
    anchors = questionnaire.get("anchors") or []
    selections = [(anchor, selection) for anchor in anchors
                  for selection in (anchor.get("selections") or [])]
    selection_ids = [str(selection.get("id") or "") for _anchor, selection in selections]
    anchor_ids = [str(anchor.get("id") or "") for anchor in anchors]

    with recorder.step("§1.3: the one questionnaire -- occasions with prompts, every control with "
                        "something to pick, and the project's own ids",
                        party="stack", kind="assert") as h:
        unnamed = [anchor for anchor in anchors
                   if not str(anchor.get("id") or "").strip()
                   or not str(anchor.get("prompt") or "").strip()]
        # FR-010, and this is `_read_the_lines`'s old `assert all(line.get("chips"))`, made on the
        # document that owns the pick lists now. `BUCKETS` carries labels, `OPTIONS` carries
        # options (`canon/openapi-v2.yaml`'s `Selection`); a control a stranger is shown with
        # neither is a control they cannot answer. The words themselves are the model's and nothing
        # asserts them (spec 016 FR-007).
        empty = [f"{anchor.get('id')}/{selection.get('id')} ({selection.get('control')})"
                 for anchor, selection in selections
                 if not (selection.get("options") if selection.get("control") == "OPTIONS"
                         else selection.get("buckets"))]
        unknown_control = [selection.get("control") for _anchor, selection in selections
                           if selection.get("control") not in ("BUCKETS", "OPTIONS")]
        # FR-011. `Q7` scoped an id to its stage's questionnaire until 048 -- *"ids may repeat
        # across stages"* -- and scopes it to the project now. 049 finished the job: `AnchorRef`
        # and `SelectionRef` are a bare id and `qualified()` is gone. So a duplicate id here is a
        # rule broken, and a `stage` key anywhere on this document means the wire never moved.
        repeated_anchors = sorted({i for i in anchor_ids if anchor_ids.count(i) > 1})
        repeated_selections = sorted({i for i in selection_ids if selection_ids.count(i) > 1})
        still_staged = ([f"anchor {anchor.get('id')}" for anchor in anchors if "stage" in anchor]
                        + [f"selection {selection.get('id')}"
                           for _anchor, selection in selections if "stage" in selection])
        h.record_assert({"state": "READY", "anchors": ">= 1, each with an id and a prompt",
                          "selections": "each offering a pick list",
                          "ids": "unique across the project, and never qualified by a stage"},
                         {"state": questionnaire.get("state"),
                          "introduction, recorded and asserted nowhere -- it is the model's own "
                          "sentence": questionnaire.get("introduction"),
                          "anchors": len(anchors), "selections": len(selections),
                          "anchor ids": anchor_ids, "selection ids": selection_ids,
                          "occasions per anchor, counted and never read": [
                              len(anchor.get("selections") or []) for anchor in anchors],
                          "controls": sorted({selection.get("control")
                                              for _anchor, selection in selections}),
                          "anchors missing an id or a prompt": unnamed,
                          "controls offering nothing to pick": empty})
        assert questionnaire.get("state") == "READY", (
            f"the questionnaire read answers state={questionnaire.get('state')!r} where the "
            f"overview said READY; the two are the same derivation and must agree")
        assert anchors, (
            "keel-cloud says the questions are READY and the questionnaire carries no occasion at "
            "all. One questionnaire with nothing on it is not a questionnaire a stranger can "
            "answer.")
        assert not unnamed, f"an occasion carries no id or no prompt: {unnamed}"
        assert not unknown_control, (
            f"a control is neither BUCKETS nor OPTIONS: {unknown_control}")
        assert not empty, (
            f"a control on the one questionnaire offers no pick list at all: {empty}. This is the "
            f"assertion the review card used to make about its chips, moved to the document that "
            f"owns it since keel-cloud spec 048.")
        assert not repeated_anchors and not repeated_selections, (
            f"an id repeats on the project's one questionnaire -- anchors {repeated_anchors}, "
            f"selections {repeated_selections}. `Q7` is project-wide since 048; an id that names "
            f"two controls puts one opaque id on two questions.")
        assert not still_staged, (
            f"the questionnaire still qualifies an id by a stage: {still_staged}. keel-cloud spec "
            f"049 reduced AnchorRef and SelectionRef to a bare id and deleted `qualified()`.")
        assert any(anchor.get("selections") for anchor in anchors), (
            "no occasion on the questionnaire carries a single control, so there is nothing to "
            "pick anywhere on the page")

    cards = {stage: (get_json(f"/v2/projects/{project_id}/stages/{stage}") or {})
             for stage in STAGES}
    with recorder.step("§1.3: each card carries its slice of the one questionnaire, and every line "
                        "that reads an earlier line points at one that exists",
                        party="stack", kind="assert") as h:
        known_selections = set(selection_ids)
        known_anchors = set(anchor_ids)
        numbers = {stage: {belief.get("number") for belief in _beliefs_on(card)}
                   for stage, card in cards.items()}
        dangling, outside, reads, bad_reads, resolved = [], [], [], [], []
        for stage, card in cards.items():
            for belief in _beliefs_on(card):
                chosen = belief.get("selectionId")
                if chosen:
                    (resolved if chosen in known_selections else dangling).append(
                        f"{stage}: {belief.get('heading')} -> {chosen}")
                # FR-013, keel-cloud 049 §6A.5: the founder-visible end of *one answer, two lines*.
                # `reads` itself never reaches a founder -- it is the model's own index into the
                # QUESTIONS context, resolved server-side -- and this object is what does.
                reference = belief.get("readsBelief")
                if reference:
                    where = f"{stage}: {belief.get('heading')} -> {reference}"
                    reads.append(where)
                    if (reference.get("stage") not in STAGES
                            or not isinstance(reference.get("line"), int)
                            or reference.get("line") not in numbers.get(reference.get("stage"), set())):
                        bad_reads.append(where)
            for anchor in ((card.get("questionnaire") or {}).get("anchors") or []):
                if str(anchor.get("id") or "") not in known_anchors:
                    outside.append(f"{stage}: {anchor.get('id')}")
        h.record_assert({"selections that resolve": "all of them",
                          "anchors on a card's slice": "a subset of the project's",
                          "references that resolve": "all of them"},
                         {"lines reading a control": resolved,
                          "lines whose control is on no questionnaire": dangling,
                          "slice sizes": {stage: len((card.get("questionnaire") or {}).get("anchors")
                                                      or []) for stage, card in cards.items()},
                          "anchors on a slice that the project does not carry": outside,
                          "lines measured with an earlier line": reads,
                          "references that point nowhere": bad_reads})
        assert not dangling, (
            f"a line names a control the project's one questionnaire does not carry: {dangling}. "
            f"Since 048 there is one id space (`Q7`), so a `selectionId` resolves by its bare id or "
            f"it resolves nowhere.")
        assert not outside, (
            f"a card's slice carries an occasion the project's questionnaire does not: {outside}")
        assert resolved, (
            "not one line on any of the three cards reads a control, so the questionnaire that was "
            "just written is about nothing the founder asked")
        assert not bad_reads, (
            f"a line says it is measured with another line that does not exist: {bad_reads}")

    opened = OpenedCard(page, recorder, _web_base_of(page))
    on_screen: dict[str, list[str]] = {}
    for stage in STAGES:
        opened.open(project_id, stage)
        on_screen[stage] = [str(strip.get("read_line") or "").strip()
                            for strip in opened.strips()
                            if str(strip.get("read_line") or "").strip()]
    with recorder.step("§1.3: and the founder can see it -- each approved card says what each line "
                        "is asked with", party="founder", kind="assert") as h:
        # keel-web spec 026 FR-020's one slot, three readings: the line's own question, *same pick
        # list as line N*, or *measured with the problem's line 3*. Which of the three a line draws
        # is the model's and the product's business; that one of them is drawn at all is what
        # proves the slice reached the founder and not only a JSON reader. Nothing reads the
        # sentence (spec 016 FR-007).
        h.record_assert({"cards saying what a line is asked with": ">= 1"}, on_screen)
        assert any(on_screen.values()), (
            f"not one of the three approved cards tells the founder what any line is asked with: "
            f"{on_screen}. The questionnaire is on the wire and the cards are not showing their "
            f"slice of it.")
    return {"questionnaire": questionnaire, "cards": cards, "waited_s": waited,
            "states": seen, "retried": retried}


def _agent_answers(chat, recorder, get_json, project_id, stage, *, timeout_s):
    """`Chat.wait_for_agent_turn`, plus S-004's own lesson: **when the screen stops changing, ask
    the wire why.** A chain keel-cloud refused, or a job that failed, leaves the chat reading
    *Connected* for ever, so a wait on the screen can only ever report that nobody answered
    (`runs/DRIFT.md` #37).

    Returns the turn, or -- when the wire has an answer the screen does not -- `{"stopped":
    <the wire's own words>}`, which is not a turn and which the caller treats as *this round
    produced no card*. It does **not** raise: on a live walk a stage whose job failed is a stage
    the founder can still say something else to, and `_walk_stage_live`'s bounded follow-ups are
    exactly what a founder does next. The run fails, legibly and with keel-cloud's own sentence,
    only once those are spent.
    """
    try:
        return _wait_for_turn(chat, recorder, get_json, project_id, timeout_s=timeout_s)
    except TimeoutError as exc:
        stopped = refusals.why_the_stage_stopped(get_json, project_id, stage)
        if stopped is None:
            raise
        with recorder.step(f"the wire says why the {stage} chat stopped answering",
                            party="stack", kind="note") as h:
            h.record_wire(None, stopped)
        _ = exc
        return {"stopped": stopped, "agent_reply": ""}


#: **Retired by spec 028, and kept so the lesson can be grepped for.** This was the last resort
#: wherever a live model wrote more anchors than the corpus person had stories for, and matrix run
#: 36895521843 is what it cost: the host wrote four anchors, Lullaby's revised corpus carries two
#: stories, and this sentence went under the other two. keel-cloud's INTERPRET read it correctly --
#: it is somebody saying they are *thinking of* an occasion, which is a **guess**, and a guess is
#: `BeliefStanding.guessed`'s own *"answers shown to the founder that count towards nothing"*. So
#: the five commercial picks were made, stored, shown and counted for nothing: `untested: 5` of
#: `total: 5` with `peopleAnswered: 5`, and §1.7 then blamed keel-web's panel for drawing no rows
#: it had nothing to draw.
#:
#: `harness/stranger_stories.py` replaced it with three honest paths -- this person's own matching
#: story, a sentence composed from this person's own facts, or a tapped escape. **Nothing types
#: this constant.** `tests/test_stranger_stories.py::test_the_filler_is_named_exactly_once_in_the
#: _journey_and_typed_nowhere` is the assertion that it stays that way; AGENTS.md's rule is invert
#: or move, never delete, and a deleted constant is a lesson nobody can grep for.
THE_STRANGER_SAYS = ("I am thinking of the last time this happened to me, and it went much the "
                     "way I described above.")

#: The three titles a participant page drew while **a section was a stage** -- keel-web's own
#: strings, from `journeys.md` §2.2. Since keel-cloud specs 048/049 a section is an **occasion**,
#: titled by the occasion the model named, so none of these may appear on the page at all. They are
#: written out here because the assertion is that they are *absent*: there is nothing else to read
#: them off, and a set that came from the page would be an assertion about itself.
OLD_STAGE_SECTION_TITLES = ("About your work", "About a possible tool", "About buying software")


#: **`_story_texts` stood here and is gone** (spec 028 T022). It answered *this person's stories,
#: in the corpus's order*, and the caller handed them out **by position** -- which is how the
#: corpus's app-purchase story ended up under the host's *"opened an app during a night waking"*
#: while the host's *"the last baby app you bought"* got the filler. Order was never the question.
#: `stranger_stories.plan()` is this repository's one reading of *which words this stranger types*,
#: it matches by occasion, and it still reads `PersonInputs.written()` through
#: `instructions/corpus.py` -- so there is still exactly one reading of *wrote something*.


def _their_pick(person, options: list[str]) -> tuple[str, bool]:
    """Which of the **model's own** options this corpus person picked, and whether it is theirs.

    A live run has no corpus questionnaire: the anchors and the pick lists are the host model's,
    invented from the founder's three statements, and a corpus selection id (`S2`) names nothing on
    the page. So the match is by **value**, case- and space-insensitively, across every pick the
    person made: *"3 to 4"* is theirs whichever selection the model hung it under. Where nothing
    of theirs is offered, the first option is taken -- exactly what this scenario did before spec
    021 -- and the caller records which of the two happened.

    Returns `(option, it_was_theirs)`. Never asserts: a model that offered none of the person's
    answers has written a different questionnaire, which is a finding for the bundle and not a
    failure of the journey (FR-007).
    """
    theirs = {str(v).strip().casefold() for pick in person.picks for v in pick.values}
    for option in options:
        if str(option).strip().casefold() in theirs:
            return option, True
    return options[0], False


def _invite_one_live(page, recorder, project_id: str, web_base: str, person_name: str) -> str:
    """Invite one person to **whichever role the screen actually offers**.

    Deliberately not `evals/preludes.py::invite_everyone`, which reads its role labels out of the
    corpus entry (`{role["id"]: role["label"] for role in entry.roles}`). That is right for a
    scripted run, where the script *is* the corpus, and wrong here: on a live run the roles are
    **the host's model's**, invented from the founder's own three statements, and the entry's own
    *"New parents"* is a label nothing on this page need ever have had. This repository has made
    that exact mistake
    once already, in S-010 -- *"asked a warm project for a fixture's role"* -- and the fix was the
    same one: read the label off the screen.
    """
    people = People(page, recorder, web_base)
    people.open(project_id)
    if page.locator(".role").count() == 0:
        people.switch_to_kinds_tab()
    cards = people.role_cards()
    with recorder.step("§1.4: the roles on the People page are the ones the host wrote",
                        party="founder", kind="assert") as h:
        h.record_assert({"role cards": ">= 1, each with a label"}, cards)
        assert cards, "the approved cards produced no role to ask anybody"
        assert cards[0]["label"].strip(), f"a role card has no label: {cards[0]!r}"
    label = cards[0]["label"]
    people.open_send_popup(label)
    people.fill_who(person_name, about=f"{label}, asked about one real occasion.")
    preview = people.go_to_preview()
    # FR-021, and shape only. **One** is the assertion: three sections each carrying their own
    # estimate is precisely the shape one occasion asked once removes. `N >= 10` is
    # `FormComposer`'s floor and the only arithmetic anybody may claim about it here; the anchors
    # and selections on a live page are the model's own, so no exact N is asserted (spec 016
    # FR-007).
    #
    # **This used to say `minutes` is rendered in exactly one place in the whole product and never
    # on the participant's page, and that is no longer true** (spec 026 FR-018).
    # `one-occasion-once-design.md` §4 named it as a drift rather than fixing it -- *"`journeys.md`
    # §2.1's mock shows *About 15 minutes* on the stranger's first screen and the page does not show
    # it"* -- and **keel-web spec 026 FR-004 fixed it**: `ParticipantRoute.tsx` now renders
    # `About N minutes` under the consent line, omitted entirely where the number is absent or not
    # positive. The assertion below did not move with the fact, and did not need to: it counts the
    # lines in the **founder's preview string**, which is still exactly one -- one questionnaire,
    # one estimate -- and the participant's own copy of the number is a second rendering of the
    # same one.
    with recorder.step("§1.5: the founder's preview names the minutes once",
                        party="founder", kind="assert") as h:
        minutes = People.preview_minutes(preview)
        h.record_assert({"About N minutes lines": 1, "N": ">= 10"}, {"found": minutes})
        assert len(minutes) == 1, (
            "the preview must carry exactly one 'About N minutes' line -- one questionnaire, one "
            f"estimate; found {minutes}")
        assert minutes[0] >= 10, f"FormComposer's floor is ten minutes; the preview said {minutes}"
    url = people.generate_link(person_name.split()[0])
    people.close_popup()
    return url


def _answer_whatever_is_asked(browser, recorder, url: str, person, entry) -> dict:
    """The corpus person answers **the questions the page actually asks**, in their own context.

    `ParticipantPage.answer_as(person, entry)` resolves a corpus person's answers against the
    *corpus's* own anchor and selection prompts. On a live project there is no corpus
    questionnaire: the anchors are the ones the host wrote, and every one of that method's
    `offers(prompt)` checks would fail silently into `skipped`, submitting an empty page. So this
    reads the rendered page instead -- the same move S-004 makes with `_page_choice`, for the same
    reason: *what is offered is the page's to say.*

    What spec 021 changed is **whose words go into it**. A selection is answered with the corpus
    person's own value wherever the model's option list offers it; where it does not, the first
    option is taken and the bundle says which answers were theirs and which were the fallback.

    **What spec 028 changed is that the stranger stopped lying about having an occasion.** The
    story under the nth anchor used to be that person's own nth story, by position, with a filler
    sentence under every anchor past the end -- and run 36895521843 is what that cost: four anchors
    written, two stories carried, two fillers typed, every one of them read as a **guess** by
    keel-cloud's INTERPRET, and the whole COMMERCIAL stage left `untested: 5` with five people
    answered. `harness/stranger_stories.py` plans every anchor instead: this person's own
    **matching** story, a first-person sentence composed from this person's own facts, or an honest
    tap. Nothing about the words is asserted -- what leg two needs from the stranger is that a real
    answer reached keel-cloud and produced a reading (FR-007) -- but the bundle now says, per
    anchor, which of the three paths it took and where every part of it came from.

    **The picks are decided before the story is typed, and that is load-bearing** (spec 028
    FR-010). A composed sentence is written *from* the ticks about to be made, so a stranger whose
    story contradicts their own answers is impossible rather than merely unlikely. The decision is
    `_their_pick`'s, unchanged.
    """
    context = browser.new_context()
    try:
        page = context.new_page()
        participant = ParticipantPage(page, recorder)
        participant.open(url)
        # ------------------------------------------------ §2.1 the opening screen, and the gate
        # keel-web 042 (the Keel Interview, 2026-10-02) put a screen in front of the questions:
        # the research-interview header, the server's own introduction, the consent block, the
        # facts line -- and **Begin**. The assertions the single scroll made about *what a stranger
        # sees* (the introduction, the consent text, the skip affordance) are made here, where the
        # product draws them now, plus the gate itself: a gate nobody presses is a questionnaire
        # nobody reaches, which is exactly how this leg failed on 2026-10-03.
        # Nothing here asserts a word the model wrote (spec 016 FR-007) -- the header and the
        # button are keel-web's own constants, and the introduction and the consent block are read
        # and counted, never matched.
        with recorder.step("§2.1: the stranger lands on the Keel Interview's opening screen",
                            party="participant", kind="assert") as h:
            opening = participant.opening()
            h.record_assert(
                {"the header says what this page is": INTERVIEW_HEAD_WHAT,
                 "an introduction": "non-empty",
                 "the consent block": ">= 1 line",
                 "the skip affordance": "on the facts line",
                 "one gate": f"{INTERVIEW_BEGIN!r} or {INTERVIEW_CONTINUE!r}"},
                opening)
            assert opening["head"]["what"] == INTERVIEW_HEAD_WHAT, (
                "the interview's header must say what this page is; it reads "
                f"{opening['head']['what']!r}")
            assert opening["introduction"].strip(), (
                f"the opening screen said nothing about who is asking or what about: {url}")
            assert opening["consent"]["lines"], (
                "a stranger is told what happens to their answers before they answer any of them "
                "(P8); the consent block drew no lines at all")
            assert "skip" in opening["facts"].lower(), (
                "the facts line is where a stranger reads that any question can be skipped; it "
                f"reads {opening['facts']!r}")
            assert opening["button"] in (INTERVIEW_BEGIN, INTERVIEW_CONTINUE), (
                f"the opening screen's one button reads {opening['button']!r}, which is neither "
                f"{INTERVIEW_BEGIN!r} nor {INTERVIEW_CONTINUE!r}")
        participant.begin()
        # --------------------------------------- the whole interview, read before a word is typed
        # One occasion is one screen since 042, so the questions cannot be read off the page at
        # once: `questionnaire()` walks the pager read-only, collects every occasion and every
        # option list the page drew, and comes back to part one. The walk is what
        # `stranger_stories.plan` needs -- its matching is **global** (the highest-scoring pair
        # anywhere in the grid first, each corpus occasion spent at most once), and matching part
        # by part would put one person's story under two occasions, which is the fault spec 028
        # exists to end.
        parts = participant.questionnaire()
        drawn = [anchor for part in parts for anchor in part["anchors"]]
        with recorder.step("§2.1: the stranger's page carries the questions the host wrote",
                            party="participant", kind="assert") as h:
            h.record_assert({"anchors": ">= 1"}, {"parts": len(parts), "anchors": drawn})
            assert drawn, f"the invitation link rendered no questions at all: {url}"
        # FR-021, and shape only: **a section is an occasion**, not a stage (keel-cloud specs
        # 048/049). One section title per anchor block, and none of the three titles a stage used
        # to draw. The titles themselves are the model's own words and nothing asserts them --
        # spec 016 FR-007 -- so this is a count and a set difference and no more. Under 042 a
        # section is also one **part** of the pager, so this is the same claim counted on the page
        # the product actually draws.
        with recorder.step("§2.1a: one section per occasion, and no stage titles left",
                            party="participant", kind="assert") as h:
            sections = participant.sections()
            stage_titles = {t.strip().lower() for t in OLD_STAGE_SECTION_TITLES}
            h.record_assert({"sections": len(drawn), "stage titles": 0},
                            {"sections": sections, "anchor blocks": len(drawn),
                             "parts the pager drew": len(parts)})
            assert len(sections) == len(drawn), (
                f"the page drew {len(sections)} section titles for {len(drawn)} anchor blocks -- "
                "one occasion is one section")
            offending = [t for t in sections if t.strip().lower() in stage_titles]
            assert not offending, (
                f"the page still titles a section by a stage: {offending}. A section is an "
                "occasion since keel-cloud spec 048")
        # ----------------------------------------------- every tick decided, before a word is typed
        # Read-only, and the read is the walk's own: `questionnaire()` carries each selection's
        # option rows exactly as the page drew them, and `_their_pick` chooses among them. Nothing
        # was clicked but Next and Back and nothing was filled, so the page the second pass types
        # into is the page this one measured.
        prompts = [(anchor.get("prompt") or "") for anchor in drawn]
        live = [i for i, prompt in enumerate(prompts) if prompt]
        chosen: dict[int, list[tuple[str, str, bool]]] = {}
        for i in live:
            rows = []
            for selection in drawn[i].get("selections") or []:
                options = (drawn[i].get("options") or {}).get(selection) or []
                if not options:
                    continue
                option, was_theirs = _their_pick(person, options)
                rows.append((selection, option, was_theirs))
            chosen[i] = rows

        # ------------------------------------------------------- one plan per anchor, then typing
        plans = stranger_stories.plan(
            [prompts[i] for i in live], entry, person.person,
            {n: [(selection, option) for selection, option, _ in chosen[i]]
             for n, i in enumerate(live)})

        # The typing pass walks the pager a second time, because an anchor is typed on the screen
        # that draws it: `ParticipantPage.offers` answers for the screen showing and no other. So
        # the loop is by part, in the page's own order, and *Next* is pressed between them --
        # including over a part with nothing of this person's on it.
        by_part: dict[int, list[int]] = {}
        for n, i in enumerate(live):
            by_part.setdefault(drawn[i].get("part") or 1, []).append(n)

        answered, picked, theirs_used, fell_back = [], [], [], []
        for part in parts:
            for n in by_part.get(part["part"], []):
                i = live[n]
                plan, prompt = plans[n], prompts[i]
                participant.tell_story(prompt, plan.text, plan.tap)
                answered.append({"prompt": prompt[:60], "said": (plan.text or "")[:200] or None,
                                  "tapped": plan.tap, "path": plan.path,
                                  "part": part["counter"] if "counter" in part
                                          else f"{part['part']} of {part['of']}",
                                  "whose": (person.person if plan.path != stranger_stories.COMPOSED
                                            else f"{person.person}'s own facts, composed")})
                (theirs_used if plan.path == stranger_stories.THEIR_OWN_STORY
                 else fell_back).append(f"anchor: {prompt[:50]} ({plan.path})")
                if plan.tap:
                    # A tap is an answer of its own and it dims that anchor's picks (`class="picks
                    # off"`) -- the product's rule, not this harness's. Ticking behind it would be
                    # answering a question the page has stopped asking.
                    picked.extend(f"{selection[:40]} -> not ticked: the anchor is tapped "
                                  f"{plan.tap}" for selection, _, _ in chosen[i])
                    continue
                for selection, option, was_theirs in chosen[i]:
                    participant.pick(selection, [option], anchor_prompt=prompt)
                    picked.append(f"{selection[:40]} -> {option}"
                                  + ("" if was_theirs else "  (the page's own first option; none "
                                                            "of this person's answers was offered)"))
                    (theirs_used if was_theirs else fell_back).append(f"pick: {selection[:44]}")
            if part["part"] < part["of"]:
                participant.next_part()
        # The last part's primary is *Send my answers* (042), and what answers it is the completion
        # screen -- *That's it.* over *"… your answers have gone to <founder>"*, which is the one
        # sentence on this page that means **stored** (`ParticipantPage.send`'s own note).
        sent = participant.submit()
        with recorder.step(f"§2.3: {person.person} sent their answers",
                            party="participant", kind="assert") as h:
            paths = {path: sum(1 for plan in plans if plan.path == path)
                     for path in stranger_stories.PATHS}
            h.record_assert({"anchors answered": len(live),
                              "anchors answered with the filler": 0,
                              "the completion screen": INTERVIEW_DONE_TITLE},
                             {"what the stranger did with each anchor the host wrote":
                                  stranger_stories.typed(plans),
                              "paths taken": paths,
                              "answered": answered, "picked": picked,
                              "the completion screen": sent,
                              "the corpus person's own words and answers, used": theirs_used,
                              "the model asked what the corpus did not, so the page's own answer "
                              "was taken": fell_back})
            assert answered, "the stranger typed nothing anywhere"
            # 042's last screen. `send()` already waited on the one clause that means *stored*;
            # this is the other half of what the stranger is left looking at, and it is the whole
            # of what sits between the send and the founder's own screens.
            assert sent["title"] == INTERVIEW_DONE_TITLE, (
                f"the interview ended on {sent['title']!r}, not on the completion screen's own "
                f"{INTERVIEW_DONE_TITLE!r}")
            # **Not an assertion about words** (FR-007). It is an assertion about *this harness*:
            # every anchor the host drew got a story or a tap, and the retired filler went into
            # none of them. A referee that types a guess cannot then fail the product for not
            # counting it (spec 028, run 36895521843).
            silent = [a["prompt"] for a in answered if not a["said"] and not a["tapped"]]
            assert not silent, f"the stranger left an anchor blank and untapped: {silent}"
            fillers = [a["prompt"] for a in answered
                       if (a["said"] or "").startswith(THE_STRANGER_SAYS[:40])]
            assert not fillers, (
                f"the retired filler reached the page under {fillers} -- keel-cloud reads it as a "
                f"guess and counts it towards nothing (spec 028 FR-017)")
        return {"answered": answered, "picked": picked, "theirs": theirs_used,
                "not theirs": fell_back, "plans": plans,
                "typed": stranger_stories.typed(plans)}
    finally:
        context.close()


def _web_base_of(page) -> str:
    from urllib.parse import urlsplit
    parts = urlsplit(page.url)
    return f"{parts.scheme}://{parts.netloc}"


# --------------------------------------------------------------------------------- the scenario

@pytest.mark.bundle(BUNDLE)
def test_s012_journey_through_a_host_live(stack, founder_one, browser, run_dir):
    ready = agent_host.readiness(HOST)
    if not ready["ok"]:
        pytest.skip(ready["reason"])

    recorder = Recorder(run_dir)
    # Spec 017: the stack's own addresses -- `http://localhost:<port>` on the eval and playground
    # profiles, the twin's URLs on `remote` -- and the founder this run signs in as: the built-in
    # Eval Founder locally, a founder registered for this cell against the twin's gated chooser.
    web_base = stack.web_base_url
    cloud_base = stack.cloud_base_url
    cell_label = (f"{remote.cell_name()} · {HOST} · journey ({LEGS}) · "
                  f"{time.strftime('%Y-%m-%d', time.gmtime())}")
    # The short name -- what keel-web greets the founder by and the project list shows -- carries
    # the journey's length too (the founder, 2026-09-13: a full run and a short run of the same
    # cell on the same day were indistinguishable inside the product; only the chooser's long
    # label said which). "Eval 0913 windows-latest-claude-py3.13 full" / "... short".
    cell_name = f"Eval {time.strftime('%m%d', time.gmtime())} {remote.cell_name()} {LEGS}"
    founder_one = remote.identity_to_sign_in_as(stack, cell_label, fallback=founder_one,
                                                name=cell_name)
    started = _now()
    passed = False
    context = browser.new_context()

    # **The founder, and the one person, come from the golden corpus** (spec 021) -- through
    # `harness/corpus_script.py`, which is the same module the six scripted scenarios read the
    # same entry through. Reused rather than copied: `founder_inputs` already refuses an entry
    # with a missing statement by name, `person_inputs` already refuses a person offered an anchor
    # their role is not asked, and a second reader here would be a second chance to be wrong about
    # both. A corpus this run cannot reach raises with the directory it looked in -- never a
    # fallback to some other founder, because a bundle that quietly measured a different person is
    # worse than one that measured nobody.
    corpus, entry = corpus_script.entry_for(stack.keel_cloud, ENTRY_ID)
    founder = corpus_script.founder_inputs(entry)
    # **The entry's beliefs, roles, anchors and taps are a *script's* data and are read nowhere
    # below.** On a live run the host's model writes all four. What this run takes from the entry
    # is exactly what a founder types (the name, the market, the three statements) and exactly
    # what one person says (their story per anchor, their picks) -- and the model's half stays
    # free and shape-asserted (spec 016 FR-007).
    # The first `PEOPLE` of the entry's people, in corpus order, that the harness can type for;
    # a taps-only person is skipped by name rather than sent in with a blank page.
    people_chosen, people_skipped = corpus_script.people_to_invite(entry, PEOPLE)
    assert people_chosen, f"{entry.id} offers nobody the harness can type for"
    person = people_chosen[0]
    person_name = person.person
    people_names = [p.person for p in people_chosen]
    write_generated(run_dir, inputs={"entry": entry.id,
                                     "project": founder.project_name,
                                     "market": founder.market.country,
                                     "statements": {stage: founder.statement(stage)
                                                     for stage in STAGES},
                                     "person": person_name,
                                     "people": people_names,
                                     "people_count": len(people_chosen),
                                     "people asked for": PEOPLE,
                                     "people skipped (nothing written the harness could type)":
                                         people_skipped,
                                     # The corpus's own stories, before the matcher sees a single
                                     # host prompt: what each person brought, in the corpus's own
                                     # order, with its anchoring. Which anchor each one lands under
                                     # is §2.3's record and not this one's (spec 028).
                                     "their stories": {
                                         p.person: [{"anchor": a.anchor_id, "text": a.text,
                                                     "tap": a.tap} for a in p.anchors]
                                         for p in people_chosen},
                                     "their picks": {p.person: {k.selection_id: k.values
                                                                 for k in p.picks}
                                                     for p in people_chosen},
                                     "host": HOST,
                                     "legs": LEGS})
    # The sixth and seventh facts a reader of eighteen bundles needs after the five repositories:
    # whose founder walked it, and how far.
    write_block(run_dir, "journey", {
        "entry": entry.id, "entry_sha256": entry.sha256, "title": founder.project_name,
        "person": person_name, "people": people_names, "people_count": len(people_chosen),
        "legs": LEGS, "install": (agent_host.NO_INSTALL if KEELS_AI else INSTALL),
        "door": ("Keel's own AI, through the Google sign-up door (spec 024): no host CLI, no "
                 "plugin, no skill, no runtime" if KEELS_AI else
                 f"the founder's own AI, through {HOST}"),
        "legs, what that means": (
            "the host leg entire, plus the first model job -- the PROBLEM frame's confirmation "
            "card -- and then the way out" if SHORT else
            f"both legs: three stages framed, reviewed and approved, the project's one "
            f"questionnaire waited for until the overview read questionsState READY and then "
            f"read whole (keel-cloud spec 048 -- a run taken before keel-e2e-eval spec 026 "
            f"says nothing here about the questionnaire, because it did not wait for one), "
            f"{len(people_chosen)} people invited and answered, the reading read, the brief "
            f"written, the overview and one card opened"),
        "corpus": str(corpus.directory)})

    keel_home = run_dir / "keel-home"
    # ...and the host's own home beside it -- `claude-home`, `copilot-home`, `codex-home`. On the
    # Keel door there is no host and therefore no home, and the name it *would* have had is
    # `keel-home`, which is already `KEEL_HOME`'s. Two different things must not be one directory,
    # least of all the two whose emptiness this door's evidence rests on, so it is named for what
    # it is: a directory nothing will ever be put in.
    host_home_dir = run_dir / ("no-host-home" if KEELS_AI else f"{HOST}-home")
    artifacts = run_dir / HOST
    model = (os.environ.get(RUNTIME_MODEL_ENV_FOR_HOST.get(HOST, ""))
             or RUNTIME_MODEL_FOR_HOST[HOST])
    # keel-cloud `canon/designs/model-routing-design.md` §6: from keel-runtime 0.5.0 the model a
    # job runs on comes from the job's own `model` key -- the cloud's table, else the CLI's
    # default -- and the `KEEL_<HOST>_MODEL` variables are not read. So on that runtime the
    # referee pins nothing and says so, rather than recording a pin the runtime never saw; the
    # table itself is read off the keel-cloud checkout (its resource, the source of truth) and
    # `None` while the cloud has no table yet.
    runtime_stamp = stack_runtime.bundled_runtime_version(stack)
    routing_runtime = models_mod.reads_the_job_key(runtime_stamp or "")
    routing_table = models_mod.from_keel_cloud(stack.keel_cloud)
    if routing_runtime:
        model = None
    host_model = next((os.environ[name] for name in HOST_MODEL_ENV if os.environ.get(name)),
                      HOST_MODEL_FOR_HOST[HOST])
    # C-5 again: an unpinned run measures the router, not a model. It is still allowed -- spec 005
    # shipped exactly that -- but the bundle must never imply a pin that was refused. On Copilot
    # both probes are free (`-p ""` is refused before inference), so this costs nothing to be sure
    # of; on Claude there is no free probe and `model_accepted` says so rather than pretending,
    # which is why an unpinned Claude run (the default) never reaches either branch.
    if model and not agent_host.host_type(HOST).model_accepted(model):
        with recorder.step("C-5: `--model` refuses the runtime's slug on this account, so that "
                            "half of the run is unpinned and says so",
                            party="stack", kind="note") as h:
            h.record_wire({"slug": model, "whose": "the runtime's"}, {"pinned": None})
        model = None
    if host_model and not agent_host.host_type(HOST).model_accepted(host_model):
        with recorder.step("C-5: `--model` refuses the host's slug on this account, so that half "
                            "of the run is unpinned and says so",
                            party="stack", kind="note") as h:
            h.record_wire({"slug": host_model, "whose": "the host's"}, {"pinned": None})
        host_model = None

    host = agent_host.build_host(HOST, home=host_home_dir, keel_home=keel_home,
                                 base_url=cloud_base, artifacts=artifacts,
                                 model=host_model, runtime_model=model,
                                 install=INSTALL)
    host.write_home_config()
    credential = host.credential_plan()
    # **versions.json says which host, which CLI and which models** (spec 019). The run_dir fixture
    # has already written the five repositories this run stood on; this adds the sixth thing a
    # matrix cell is defined by and a reader of eighteen bundles needs first.
    write_host(run_dir, {"host": HOST, "cli": ready["version"], "binary": host.binary,
                         "home_var": host.home_var, "home": str(host_home_dir),
                         "work_dir": str(host.work_dir),
                         "executor expected": EXPECTED_EXECUTOR,
                         "model (the host's own --model)": host_model,
                         "model (the runtime's)": model,
                         "model (the runtime's), how": (
                             f"keel-runtime {runtime_stamp} takes each job's model from the "
                             f"job's own `model` key (keel-cloud's model-routing table"
                             f"{', absent on this checkout' if routing_table is None else ''}, "
                             "else the CLI's default); nothing is pinned by this referee"
                             if routing_runtime else
                             f"pinned through {RUNTIME_MODEL_ENV_FOR_HOST.get(HOST)}" if model else
                             "not pinned -- this host's executor takes no model, so the bundle "
                             "records what answered instead"),
                         "model routing table": (
                             {"source": routing_table.source, "version": routing_table.version,
                              "row for this host": routing_table.hosts.get(HOST) or {},
                              # keel-cloud table v6 (spec 047): the second half of the pin, from
                              # the same host x tier coordinate. Recorded, never set -- what the
                              # runtime passes to its CLI is the cloud's choice, and a bundle that
                              # named the model without the effort would name half of what ran.
                              "effort row for this host": (routing_table.efforts or {}).get(HOST) or {},
                              "classes": routing_table.classes}
                             if routing_table else None),
                         "credential": credential,
                         # spec 024 FR-002/FR-013: on the Keel door the two names are different
                         # words about different subjects, and a reader gets both.
                         "door": (("Keel's own AI (keel-cloud spec 045). `keel` is the door, the "
                                   "cell id and this bundle's name; `api` is what keel-cloud's "
                                   "own executor reports as `execution.host`, because there is no "
                                   "CLI and no host -- only an HTTP client against a provider.")
                                  if KEELS_AI else f"the founder's own AI, through {HOST}"),
                         "cli, why": ("there is no host CLI on this door, so there is no version "
                                      "to record" if KEELS_AI else None),
                         "install": (agent_host.NO_INSTALL if KEELS_AI else INSTALL)})

    def _get(path: str) -> dict:
        return context.request.get(f"{cloud_base}{path}", timeout=20_000).json()

    def _post(path: str) -> dict:
        """The one POST this journey makes to keel-cloud directly, and it exists for one button:
        *Try again* beside a locked People entry (keel-web spec 026 FR-019). Every other act of
        this journey goes through the screen, because the screen is what is under referee; this one
        is a founder's single click on a control whose whole content is that it was clicked, and
        driving it through the side nav would mean waiting for a `FAILED` to render before the
        wire's own `FAILED` could be acted on."""
        response = context.request.post(f"{cloud_base}{path}", timeout=20_000)
        try:
            body = response.json()
        except Exception:  # noqa: BLE001 - a 422 carries a Refusal; anything else is evidence too
            body = {"text": response.text()[:400]}
        return {"status": response.status, **(body if isinstance(body, dict) else {"body": body})}

    def _status() -> dict:
        return stack_runtime.status(stack, home=keel_home)

    #: What the Keel door's jobs reported, filled once they exist. Held out here so the bundle's
    #: one-line fact can be written from `finally` on a run that died at any point -- an empty
    #: list is itself the true thing to say about a run that never got a job answered.
    door_jobs: list[dict] = []
    #: How long the founder waited for the problem to be framed and broken into lines, by **this
    #: harness's own clock** -- the one timing that is always available, because keel-cloud's
    #: `execution` report carries none and a job row's timestamps are whatever it happens to put
    #: there (spec 024, the founder's effort comparison: the number has to be readable off the
    #: bundle without opening a database). `None` on a run that never got that far.
    framing_took_s: float | None = None

    def _the_keel_door_in_one_line() -> str:
        """`facts.json`'s one string on this door (spec 024 FR-013), in the shape the other three
        doors' line has: who answered, through what, and with which models."""
        models = sorted({str(row.get("model_used")) for row in door_jobs if row.get("model_used")})
        return ("keel · Keel's own AI, through the Google sign-up door · no host CLI, no plugin, "
                f"no runtime · the wire reports execution.host={EXPECTED_EXECUTOR!r} · "
                + (f"models {', '.join(models)}" if models else
                   "no job of this journey reported a model"))

    def _what_the_framing_measured() -> str:
        """**The effort comparison, on one line, in `facts.json`** (spec 024, the founder,
        2026-09-29: *"at different effort settings"*).

        keel-cloud chooses the effort (`output_config.effort`, **`medium`** by default since
        2026-09-30 -- spec 047, run of record `20260930T024851Z-instructions`; `xhigh` under spec
        045 FR-017 before it) and this repository pins none: two runs of this cell against two
        settings differ by what keel-cloud was configured with, and what a reader needs is the pair
        of numbers each one produced. **Pinning none is more important now, not less**: since
        keel-cloud table v6 the effort a CLI host's own runtime runs at also comes from that table,
        on the job wire's `effort` key, so a cell that exported `CLAUDE_CODE_EFFORT_LEVEL` would be
        overriding the very thing this run exists to observe -- which is why `scrub_session`'s
        `CLAUDE_CODE_` prefix sweep is load-bearing rather than hygienic. So the line carries the models that answered, what keel-cloud says it paid,
        and how long the founder waited -- all three readable off the bundle without opening a
        database, which is the whole point of putting it here rather than in `spend.json` alone.

        **There are no token counts, and their absence is said rather than filled in.** keel-cloud's
        `execution` object is five strings, a boolean and the cost; tokens are not on that wire at
        all (spec 045 FR-023 computes the cost *from* usage and reports only the cost).
        """
        models = sorted({str(row.get("model_used")) for row in door_jobs if row.get("model_used")})
        micro = sum(row.get("actual_cost_micro_usd") or 0 for row in door_jobs)
        waited = ("unknown -- the framing never finished" if framing_took_s is None
                  else f"{framing_took_s:.1f}s")
        return (f"{len(door_jobs)} job(s) · "
                + (f"models {', '.join(models)}" if models else "no model reported")
                + f" · {micro:,} µUSD (${micro / 1_000_000:.4f}) of Keel's own inference"
                + f" · the founder waited {waited}"
                + " · tokens: not on the wire (keel-cloud reports cost, not usage)"
                + " · effort: keel-cloud's own `output_config.effort`, pinned by nothing here")

    def _me() -> dict:
        return _get("/v2/me") or {}

    def _credits_now() -> int | None:
        value = _me().get("creditsAvailable")
        return value if isinstance(value, int) and not isinstance(value, bool) else None

    try:
        page = context.new_page()
        auth = Auth(page, recorder, web_base)
        landing = Landing(page, recorder, web_base)

        # **The door is the whole of the message** (keel-cloud spec 044 FR-014,
        # `GoogleSignIn.doorOf`). Nothing in this harness says which AI the founder wants, because
        # there is no field that could: keel-cloud reads the door off the pre-login record's own
        # stored `return_to`. `/signup`'s is `/` and makes a KEEL account with a 1,500-credit
        # grant; the code story's is `/connect?user_code=...` and makes an OWN one. Same three
        # hops, same real callback, same stub picker -- a different screen, and therefore a
        # different account.
        #
        # **And that is why the legs are in this order now.** On the three CLI doors the founder
        # cannot sign in yet: they have no code, because they have installed nothing and said
        # nothing. So leg one runs first, the runtime prints the code, and the sign-in happens
        # where a founder's actually does -- at `/login?user_code=...`. Until spec 024 this
        # scenario signed in at the plain `/login` before leg one, which made every CLI cell a
        # KEEL account with a grant it should never have had.
        if KEELS_AI:
            auth.sign_up(founder_one)
            arrival = landing.visit()
            # ================================================ THE DOOR: what only Keel's AI shows
            with recorder.step("spec 024: the landing reads a number, not an agent -- 1,500 "
                                "credits, no agent line, and this run's KEEL_HOME is empty",
                                party="founder", kind="assert") as h:
                shell = Shell(page, recorder)
                me = _me()
                credits_line = shell.credits_line_text()
                h.record_assert({"credits line": f"{agent_host.KEELS_AI_GRANT:,} credits available",
                                  "agent line present": False,
                                  "aiPath": "KEEL",
                                  "creditsAvailable": agent_host.KEELS_AI_GRANT,
                                  "heartbeat": None},
                                 {"credits line": credits_line,
                                  "agent line present": shell.agent_line_present(),
                                  "aiPath": me.get("aiPath"),
                                  "creditsAvailable": me.get("creditsAvailable"),
                                  "agent (spec 045 FR-047: answered truthfully, and not "
                                  "connected)": me.get("agent"),
                                  "heartbeat": agent_host.read_heartbeat(keel_home),
                                  "KEEL_HOME": str(keel_home)})
                # The wire first: what the founder is shown is keel-web's reading of it, and a
                # bundle that could not tell a formatting change from a grant change would be
                # useless on the morning either happened.
                assert me.get("aiPath") == "KEEL", (
                    f"the account this run made is not on Keel's AI: /v2/me says aiPath="
                    f"{me.get('aiPath')!r}. The sign-up door is what decides it (keel-cloud spec "
                    f"044 FR-014), so either the door moved or keel-cloud read it differently.")
                assert me.get("creditsAvailable") == agent_host.KEELS_AI_GRANT, (
                    f"a new Keel's-AI account is granted {agent_host.KEELS_AI_GRANT} credits once, "
                    f"at creation (keel-cloud spec 044 FR-017); /v2/me says "
                    f"{me.get('creditsAvailable')!r}. A monthly grant budget that is already "
                    f"spent reads as 0 here, and is a finding, not a pass.")
                assert credits_line == f"{agent_host.KEELS_AI_GRANT:,} credits available", (
                    f"the shell line reads {credits_line!r}, not "
                    f"{agent_host.KEELS_AI_GRANT:,} credits available (keel-web spec 024 FR-011)")
                assert not shell.agent_line_present(), (
                    "the shell drew an agent line on Keel's AI -- keel-web spec 024 FR-011 "
                    "renders exactly one of the two, and a founder on this road has no agent to "
                    "be told about")
                assert agent_host.read_heartbeat(keel_home) is None, (
                    f"this run's KEEL_HOME already carries a heartbeat, and on this door nothing "
                    f"could have written one ({keel_home})")

            with recorder.step("spec 024: there is no leg one on this door, and it is skipped "
                                "rather than asserted loosely", party="stack", kind="note") as h:
                h.record_wire({"host": HOST, "install": agent_host.NO_INSTALL},
                               {"not run": ["the marketplace and the plugin install",
                                            "the CLI's own skill listing",
                                            'the founder saying "keel connect"',
                                            "the device code, the /connect approval and "
                                            "`already_connected`",
                                            "the runtime's `KEEL_EXECUTOR=` startup line",
                                            "keel-connect-skill's own way out"],
                                "why": ("keel-cloud `ai-credits-design.md` §6: the door decides "
                                        "the AI. A founder who signs up with Google installs "
                                        "nothing and runs nothing; keel-cloud answers every job "
                                        "on its own account (spec 045)."),
                                "how it is kept honest": (
                                    "`harness/keel_host.py` raises `NoHostHere` from every one of "
                                    "those methods, so a future edit that reached for leg one on "
                                    "this door gets a sentence and not an empty result"),
                                "credential": credential})
        else:
            # **§1.0's other half, and it happens before anybody signs in now.** Until spec 024
            # this was one step read off the landing, which meant signing in first -- and signing
            # in first is exactly what put these cells through the wrong door. The half that needs
            # a session (*no agent connected*) moves down to where the session is; this half is a
            # filesystem read and is now made **earlier** than it was, before one command has run.
            with recorder.step("§1.0: this run's own homes are empty before a word is said",
                                party="stack", kind="assert") as h:
                h.record_assert({"heartbeat": None, "launch log": ""},
                                 {"heartbeat": agent_host.read_heartbeat(keel_home),
                                  "launch log": agent_host.read_launch_log(keel_home)[:200],
                                  "KEEL_HOME": str(keel_home),
                                  host.home_var: str(host_home_dir)})
                assert agent_host.read_heartbeat(keel_home) is None, (
                    f"this run's KEEL_HOME already carries a heartbeat before {HOST} has said a "
                    f"word")

        # ======================================================= LEG ONE: the host that loads it
        if KEELS_AI:
            first = second = None
        else:
            with recorder.step(f"leg one: how this {HOST} is authenticated, and which model it pins",
                                party="stack", kind="note") as h:
                h.record_wire({host.home_var: str(host_home_dir)},
                               {"credential": credential,
                                "cli": ready["version"],
                                "pinned_model (the host's own --model)": host_model,
                                "pinned_model (the runtime's)": model,
                                "why they differ": ("runs/DRIFT.md #59 -- on Copilot the plan's "
                                                    "default model answers correctly and keel-runtime "
                                                    "cannot read it, so the host keeps the founder's "
                                                    "own default and the runtime pins one it can "
                                                    "read. On Claude the runtime's executor takes no "
                                                    "model at all, so there is nothing to pin and the "
                                                    "bundle records what answered."),
                                "KEEL_RUNTIME_PATH in the child": "scrubbed (T-1)",
                                "the session this harness runs in": "scrubbed, so the skill's own "
                                                                    "host detection sees one host"})

            if INSTALL == "speckit":
                # The Spec Kit road (spec 022): the extension `make dist` wrote, added to a Spec Kit
                # project in the host's own working directory, and the commands Spec Kit registers
                # as this host's project skills. Built here when the checkout has no dist/ yet.
                source_tree = stack.keel_connect_skill / "dist" / "speckit"
                if not (source_tree / "extension.yml").is_file():
                    subprocess.run(["make", "-C", str(stack.keel_connect_skill), "dist"],
                                   check=True, capture_output=True, timeout=300)
                with recorder.step("leg one: the Spec Kit extension is added to a project, with "
                                    "Spec Kit's own two commands", party="stack", kind="assert") as h:
                    installed = host.install_extension(source_tree)
                    h.record_wire({"source": str(source_tree), "work_dir": str(host.work_dir)},
                                   installed)
                    assert installed["exit_code"] == 0, (
                        f"`{' '.join(installed['cmd'])}` failed: "
                        f"{installed['stderr'] or installed['stdout']}")

                with recorder.step(f"leg one: {HOST} sees {agent_host.EXTENSION_SKILL_NAME}, as a "
                                    "project skill Spec Kit registered", party="stack", kind="assert") as h:
                    proof = host.extension_proof()
                    h.record_assert({"skill file": "present", "listed by specify": True},
                                     {"found": proof["found"], "listed": proof["listed"],
                                      "skill_file": proof["skill_file"], "raw": proof["raw"]})
                    assert proof["found"], (
                        f"Spec Kit did not register {agent_host.EXTENSION_SKILL_NAME!r} at "
                        f"{proof['skill_file']}")
                    assert proof["listed"], (
                        f"`specify extension list` does not name keel: {proof['raw'][:800]!r}")
            else:
                with recorder.step("leg one: the plugin is installed from the real marketplace with "
                                    f"{HOST}'s own two commands", party="stack", kind="assert") as h:
                    added = host.add_marketplace()
                    installed = host.install_plugin()
                    h.record_wire({"marketplace": agent_host.MARKETPLACE_SOURCE,
                                    "plugin": agent_host.PLUGIN_SPEC},
                                   {"add": added, "install": installed,
                                    "list": host.plugin_list()})
                    assert added["exit_code"] == 0, (
                        f"`{' '.join(added['cmd'])}` failed: {added['stderr'] or added['stdout']}")
                    assert installed["exit_code"] == 0, (
                        f"`{' '.join(installed['cmd'])}` failed: "
                        f"{installed['stderr'] or installed['stdout']}")

                with recorder.step(f"leg one: {HOST} sees keel-connect, and as a plugin skill",
                                    party="stack", kind="assert") as h:
                    proof = host.skill_proof()
                    h.record_assert({"skill": agent_host.SKILL_NAME, "source": "a plugin"},
                                     {"found": proof["found"], "from a plugin": proof["from_plugin"],
                                      "detail": proof["detail"], "raw": proof["raw"][:4000]})
                    assert proof["found"], (
                        f"`{' '.join(proof['cmd'])}` does not name {agent_host.SKILL_NAME!r} after the "
                        f"plugin installed cleanly: {proof['raw'][:1000]!r}")
                    assert proof["from_plugin"], (
                        f"{agent_host.SKILL_NAME!r} is visible but not as a plugin skill: "
                        f"{proof['detail']!r}")

            with recorder.step(f'leg one: the founder says "keel connect" to {HOST}, once',
                                party="founder", kind="protocol") as h:
                first = host.say(THE_FOUNDER_SAYS, slug="connect-1")
                h.record_wire({"argv": first.argv, "cwd": str(host.work_dir)},
                               {"exit_code": first.exit_code, "model": first.model,
                                "spend": first.spend(),
                                "tools": first.tools_used,
                                "reply": first.reply_text[:4000],
                                "stderr": first.stderr[:2000],
                                "transcript": str(first.transcript_path)})

            with recorder.step("leg one: a runtime is really there -- the heartbeat says "
                                "`awaiting_approval`", party="stack", kind="assert") as h:
                heartbeat = agent_host.read_heartbeat(keel_home)
                h.record_assert({"state": agent_host.STATE_AWAITING_APPROVAL,
                                  "pid": "a live one", "agent_session_id": None},
                                 heartbeat)
                assert heartbeat is not None, (
                    f"{HOST} answered but no runtime heartbeat exists under this run's KEEL_HOME "
                    f"({keel_home}) -- so nothing was started, whatever the reply said. It said: "
                    f"{first.reply_text[:400]!r}")
                assert heartbeat.get("state") == agent_host.STATE_AWAITING_APPROVAL, (
                    f"expected a runtime waiting for device approval, the heartbeat reads "
                    f"{heartbeat.get('state')!r}")
                assert heartbeat.get("pid"), f"the heartbeat names no pid: {heartbeat!r}"

            with recorder.step("leg one: the launch log carries the code and the device page URL",
                                party="stack", kind="assert") as h:
                log_text = agent_host.read_launch_log(keel_home)
                user_code = agent_host.user_code_in(log_text)
                verification_uri = agent_host.verification_uri_in(log_text)
                h.record_assert({"KEEL_USER_CODE=": "XXXX-XXXX",
                                  "KEEL_VERIFICATION_URI=": f"{web_base}/connect"},
                                 {"user_code": user_code, "verification_uri": verification_uri,
                                  "log": log_text[:2000]})
                assert agent_host.looks_like_a_user_code(user_code), (
                    f"no `KEEL_USER_CODE=` line of the right shape in {keel_home}/"
                    f"{agent_host.LAUNCH_LOG_FILENAME}: {log_text[:500]!r}")
                assert verification_uri and verification_uri.startswith(f"{web_base}/connect"), (
                    f"the launch log's verification URI is not this stack's own /connect: "
                    f"{verification_uri!r}")

            # ==================== THE DOOR, on the three CLI roads: the code story (spec 024)
            # keel-cloud spec 044 FR-014, `GoogleSignIn.doorOf`: the door an account is **made**
            # on is read back off the pre-login record's own stored `return_to`, and `/connect` is
            # the ONLY path that answers `OWN`. Everything else -- including the bare `/` this
            # scenario signed in with until today -- answers `KEEL`, grants 1,500 credits, and
            # (once keel-cloud spec 045 lands) hands that founder's jobs to Keel's own Anthropic
            # key instead of to the CLI this cell has just installed. Eight weekly cells would
            # have been spending the company's money on a founder who brought their own.
            #
            # So the founder signs in where a founder actually does: their AI printed a code, and
            # they take it to `/login?user_code=...` -- the code story, *Continue with Google*,
            # which keel-web spec 024 FR-005 leaves byte for byte alone -- carrying
            # `/connect?user_code=...` as the `return_to`.
            landed = auth.sign_in_with_code(founder_one, user_code)
            with recorder.step("§10.6: the code survived the login -- the founder comes back to "
                                "the approval screen, not to the project list",
                                party="founder", kind="assert") as h:
                h.record_assert({"landed on": f"/connect?user_code={user_code}"}, landed)
                assert "/connect" in landed["landed"] and user_code in landed["landed"], (
                    f"the sign-in that carried {user_code!r} came back to {landed['landed']!r}. "
                    f"keel-cloud stores the `return_to` at `start` and brings the founder back to "
                    f"it, so a landing anywhere else means the code did not travel -- and the "
                    f"account this run just created is on the wrong side of `GoogleSignIn.doorOf`.")

            arrival = landing.visit()
            with recorder.step("§1.0: the landing reads no agent connected -- the runtime is "
                                "waiting for this founder to approve it",
                                party="founder", kind="assert") as h:
                agent_line = Shell(page, recorder).agent_line_text()
                h.record_assert({"agent_connected": False},
                                 {"agent_connected": arrival["agent_connected"],
                                  "agent line": agent_line,
                                  "heartbeat": agent_host.read_heartbeat(keel_home)})
                assert not arrival["agent_connected"], (
                    f"expected no agent connected yet, got {agent_line!r}")

            # One reader for every scenario that connects a runtime (spec 024), so the journey and
            # the corpus riders cannot quietly stop meaning the same thing about the same door.
            own_ai_door(page, recorder, stack, _get, through_the_code_story=True)

            # **And this read needs the session, which is why it is here and not above.**
            # keel-cloud's `SecurityConfig` gates `GET /v2/device-authorizations` on a founder
            # session (spec 023 FR-001: *"a runtime has no credential yet when it starts or polls
            # a device authorization, but only the founder's own browser ever reads one back by
            # code"*) -- the two POSTs on the same base path are `permitAll`, the GET is not. So
            # the earliest any scenario can ask *"is this a code this Keel issued"* is after the
            # sign-in, and the sign-in is now the code story's.
            with recorder.step("leg one: the code is one **this Keel** issued, and it is not approved "
                                "yet", party="stack", kind="assert") as h:
                response = context.request.get(
                    f"{cloud_base}/v2/device-authorizations?user_code={user_code}", timeout=20_000)
                body = response.json() if response.ok else {"status": response.status}
                h.record_assert({"http": 200, "approved": False},
                                 {"http": response.status, "body": body})
                assert response.ok, (
                    f"the eval cloud does not know the code {HOST} relayed ({user_code!r}): "
                    f"HTTP {response.status}. A code this Keel never issued means the skill talked to "
                    f"a different Keel, or the host invented one.")
                assert not body.get("approved"), (
                    f"the code was already approved before the founder touched it: {body}")

            connect = Connect(page, recorder)
            frame = connect.open(verification_uri)
            with recorder.step("leg one: the verification URI opens the device-decision frame",
                                party="founder", kind="assert") as h:
                h.record_assert("B", frame)
                assert frame == "B", f"expected the device-decision frame B, got {frame!r}"
                on_screen = connect.user_code()
                assert user_code in on_screen, (
                    f"the screen shows {on_screen!r} where the launch log said {user_code!r}")
            connect.approve()
            connect.wait_for_connected(timeout_s=60)

            with recorder.step('leg one: the founder says "keel connect" a second time -- the skill\'s '
                                "`already_connected`", party="founder", kind="protocol") as h:
                second = host.say(THE_FOUNDER_SAYS, slug="connect-2")
                h.record_wire({"argv": second.argv},
                               {"exit_code": second.exit_code, "model": second.model,
                                "spend": second.spend(),
                                "tools": second.tools_used,
                                "reply": second.reply_text[:4000],
                                "transcript": str(second.transcript_path)})

            with recorder.step("leg one: the runtime's own `status` says connected -- and the host's "
                                "reply says so too (loosely, and never on its own)",
                                party="stack", kind="assert") as h:
                status = _status()
                said_connected = agent_host.mentions_connected(second.reply_text)
                h.record_assert({"running": True, "connected": True, "reply mentions connected": True},
                                 {"status": status, "reply mentions connected": said_connected,
                                  "reply": second.reply_text[:1000]})
                assert status.get("running"), f"the runtime is not running after approval: {status}"
                assert status.get("connected"), (
                    f"the runtime never completed device approval: {status}")
                assert said_connected, (
                    f"the runtime is connected but {HOST}'s second reply never says so, so the "
                    f"skill's `already_connected` was not relayed: {second.reply_text[:400]!r}")

            # ========= LEG TWO's one runtime question -- still the host's, so still in this arm.
            # Which executor the runtime chose is the last thing leg one proves and the first
            # thing leg two rests on, and on the Keel door there is no runtime to ask it of. What
            # answered *there* is read off keel-cloud's own `execution` report at the end of the
            # journey instead (spec 024 FR-007). Everything below this arm -- the walk, the
            # people, the reading, the brief -- is the same journey on all four doors.
            with recorder.step(f"leg two: the runtime is on the {EXPECTED_EXECUTOR} executor, because "
                                "the skill told it which host it was running under and nothing here "
                                "named an executor", party="stack", kind="assert") as h:
                # **Read off the runtime's own startup line, not off `keel status`** (`runs/DRIFT.md`
                # #58). keel-cloud's contract defines `status.executor` as *"which executor this home
                # **would** run a job with ... resolved the same way `connect` resolves it"* -- the
                # caller's resolution, not the live process's. Asked from this harness (a Claude Code
                # session, so `CLAUDECODE=1` is in the environment `resolve_executor` reads) it
                # answers `claude` about a runtime whose own log says `KEEL_EXECUTOR=copilot`. That
                # is the first thing this scenario found and it is recorded, not adapted around: the
                # `status` reading goes into the bundle beside the one that knows.
                #
                # **`source=flag` is asserted on both hosts, and it is the same chain both times.**
                # Copilot gets there because `SKILL.md` carries the one D5 exception telling it to add
                # `--host copilot`; Claude gets there because the skill's own `detect_host` reads the
                # `CLAUDECODE=1` its CLI sets for the shell it runs the script in. Either way the
                # *script* passes `--executor`, so the runtime records an explicit term -- and a run
                # that arrived at the right name by `source=path` or `source=host` would be a runtime
                # that guessed right, which proves nothing about the skill.
                launched = agent_host.launch_executor_in(agent_host.read_launch_log(keel_home))
                status = _status()
                h.record_assert({"KEEL_EXECUTOR": EXPECTED_EXECUTOR, "source": "flag"},
                                 {"the runtime's own startup line": launched,
                                  "keel status (DRIFT #58: the caller's resolution, not this "
                                  "runtime's)": {"executor": status.get("executor"),
                                                 "executor_on_path": status.get("executor_on_path")},
                                  "environment": status.get("environment")})
                assert launched is not None, (
                    f"the runtime left no `KEEL_EXECUTOR=` line in {keel_home}/"
                    f"{agent_host.LAUNCH_LOG_FILENAME}, so which executor it chose is unknowable")
                assert launched["executor"] == EXPECTED_EXECUTOR, (
                    f"the runtime is on {launched['executor']!r}, not {EXPECTED_EXECUTOR!r} -- the "
                    f"skill did not tell it which host it was running under (SKILL.md's D5 "
                    f"exception for Copilot; the script's own host detection for Claude)")
                assert launched.get("source") == "flag", (
                    f"the runtime chose {EXPECTED_EXECUTOR!r} by {launched.get('source')!r} rather "
                    f"than by an explicit term -- the skill is meant to *tell* it, so a run that "
                    f"guessed right off an environment marker has not proven the skill's line works")
                assert status.get("environment") == _environment_of(cloud_base), (
                    f"the runtime names {status.get('environment')!r}, not this stack's Keel")

            with recorder.step("C-5: the pin the skill's own launch carried -- or, on a host whose "
                                "executor takes no model, the absence of one, said out loud",
                                party="stack", kind="assert") as h:
                h.record_assert({"model": model}, {"the runtime's own startup line": launched,
                                                   "pinned": bool(model)})
                if model:
                    assert launched.get("model") == model, (
                        f"the runtime launched with model {launched.get('model')!r} where this run "
                        f"pinned {model!r}: `KEEL_COPILOT_MODEL` did not reach the executor")

        # spec 024 FR-006: the number before anything has been asked of Keel's AI. Read off the
        # wire rather than off the screen, because what is being measured is the ledger and the
        # screen is only keel-web's reading of it (`creditsAvailable` is `SUM(credits)` computed
        # at read time -- keel-cloud spec 044 FR-033, design X2).
        credits_before = _credits_now() if KEELS_AI else None

        project_id = create_project(page, recorder, web_base, founder)

        if KEELS_AI:
            with recorder.step("spec 024: a project started with no runtime bound, because a "
                                "Keel's-AI account is never asked for an agent",
                                party="founder", kind="assert") as h:
                # keel-cloud spec 045 FR-045: `POST /v2/projects`' live-agent refusal (422 rule
                # "agent", *"your AI is not connected"*) does not run for a KEEL account -- and
                # keel-web spec 024 FR-013 does not render the gate card or the lock beside *New
                # project*. So a project exists, and the fact that it exists is the assertion.
                # (Until keel-cloud spec 045 lands, this is exactly where the journey stops: spec
                # 044's own *what this pass does not do* leaves the 422 in place for a KEEL
                # account with no runtime bound, after the credit gate has already answered.)
                h.record_assert({"project": "created with no agent connected"},
                                 {"project_id": project_id,
                                  "agent": (_me().get("agent") or {}),
                                  "creditsAvailable": credits_before})
                assert project_id, "no project was created"

        credits_after_first_job = None

        def _the_number_went_down() -> None:
            """**spec 024 FR-006**, made once, after the PROBLEM framing has run.

            keel-cloud writes the `HOLD` -- `credits = −price` -- in the **same transaction as the
            job insert** (`ai-credits-design.md` §8.3, invariant X1), so the balance moves when
            the work is *started*, not when it lands: *"the number drops when the hold is written,
            not when the job ends"* (keel-cloud spec 044, US6 scenario 3). The card having landed
            is therefore well past the moment this measures, which is the point -- a strictly
            smaller number here is the ledger having charged for work Keel's AI actually did.
            """
            nonlocal credits_after_first_job
            credits_after_first_job = _credits_now()
            with recorder.step("spec 024: the credits line went down once Keel's AI did the first "
                                "framing", party="stack", kind="assert") as h:
                spent = (None if credits_before is None or credits_after_first_job is None
                         else credits_before - credits_after_first_job)
                h.record_assert({"credits after": f"< {credits_before}"},
                                 {"credits before": credits_before,
                                  "credits after": credits_after_first_job,
                                  "spent, in credits": spent,
                                  "what a framing costs, per the design": (
                                      "540 credits for all six framing kinds; the PROBLEM frame "
                                      "alone is 30 and its assumptions 155 "
                                      "(ai-credits-design.md §4.1)"),
                                  "on the screen": Shell(page, recorder).credits_line_text()})
                assert credits_before is not None and credits_after_first_job is not None, (
                    f"/v2/me answered no integer creditsAvailable on a KEEL account "
                    f"(before={credits_before!r}, after={credits_after_first_job!r}); keel-cloud "
                    f"spec 044 FR-033 makes it null only on an OWN one")
                assert credits_after_first_job < credits_before, (
                    f"Keel's AI framed the problem and the ledger did not move: "
                    f"{credits_before} -> {credits_after_first_job}. The HOLD is written in the "
                    f"same transaction as the job insert (design §8.3, X1), so a balance that "
                    f"did not drop means no job of this founder's was ever priced.")

        def _the_screens_say_keel() -> None:
            """**spec 024 FR-009**, made where the founder is actually reading (keel-web spec 024
            FR-014, `AI_SUBJECT_KEEL`).

            Twenty-seven strings say *Keel* on this road where they say *your AI* on the other
            one, all through one substitution. Pinning twenty-seven sentences here would make this
            repository a second copy of keel-web's `translate.ts` and would go red on a copy
            review the founder has not finished, so what is asserted is the **property** the
            substitution exists to produce: the chat says who it is, and the word *your AI*
            appears nowhere on the founder's own screen.
            """
            shell = Shell(page, recorder)
            with recorder.step("spec 024: the founder's screens say Keel, never *your AI*",
                                party="founder", kind="assert") as h:
                name = Chat(page, recorder).chat_name()
                stragglers = shell.says_your_ai()
                h.record_assert({"chat name": "Keel", "lines saying *your AI*": []},
                                 {"chat name": name, "lines saying *your AI*": stragglers,
                                  "credits line": shell.credits_line_text(),
                                  "agent line present": shell.agent_line_present()})
                assert name.strip() == "Keel", (
                    f"the chat calls itself {name!r} on a Keel's-AI project; keel-web spec 024 "
                    f"FR-014 makes it {'Keel'!r} behind this door")
                assert not stragglers, (
                    f"a founder on Keel's AI was told about *your AI*, which they do not have: "
                    f"{stragglers}")

        # The words, read on the screen `create_project` just landed the founder on -- the
        # project's own PROBLEM chat, before a single thing has been said to it. Asserted here
        # rather than after a stage because this is where `.chat__name` is certainly on screen,
        # and because what FR-009 is about is what a founder *arrives* to.
        if KEELS_AI:
            _the_screens_say_keel()

        # **The first model job, and on the short journey the only one** (spec 021). The founder
        # types the entry's PROBLEM statement and the host's model answers it with a confirmation
        # card. `_land_the_card` is one function, called from here and from `_walk_stage_live`, so
        # the assertion the short run makes is *the same assertion* the full run makes at the same
        # point -- not a copy of it that would have to be kept in step.
        if SHORT:
            framing_started = _now()
            chat, _first_card = _land_the_card(page, recorder, _get, project_id, "PROBLEM",
                                               founder.statement("PROBLEM"))
            if agent_host.short_reaches_the_assumptions(HOST):
                # **On a door with no host leg, one model job is not a founder-visible outcome.**
                # Spec 021's `short` is *the host leg plus the first model job*, and on the three
                # CLI doors the host leg is the thing being measured -- the install, the three
                # words, the device approval, the executor -- so a confirmation card is a fair
                # place to stop. On the Keel door there is no host leg at all, so a run that
                # stopped there would have measured a claim with no lines under it, which is not
                # something a founder ever sees. The founder's own words (2026-09-29): *"only the
                # framing-and-assumptions part -- the problem framed, broken into lines and
                # questions -- at different effort settings, to keep spend down."* That is one
                # interaction chain: `PROBLEM_FRAME` and the `PROBLEM_ASSUMPTIONS` keel-cloud
                # chains off it. `_read_the_lines` is the same function the full journey calls at
                # the same point, so the assertions are the same assertions.
                _read_the_lines(page, recorder, _get, project_id, "PROBLEM", chat)
            framing_took_s = _now() - framing_started
            if KEELS_AI:
                _the_number_went_down()
            # Nothing is asserted about *stopping*: the short journey does less, it does not do
            # something else. This is a note, and every assertion below it -- no refusals, every
            # job COMPLETED, what it cost, the founder's own way out -- is one both lengths make.
            with recorder.step("spec 021: the short journey stops here -- and on this door that is "
                                "the framing and its assumptions", party="stack", kind="note") as h:
                h.record_wire({agent_host.LEGS_ENV: LEGS, "host": HOST},
                               {"asserted": (
                                    "sign-up through the Google door, 1,500 credits and no agent "
                                    "line, a project started with no runtime bound, the problem "
                                    "framed, and the lines keel-cloud chained off it -- read "
                                    "through the same function the full journey reads them "
                                    "through. NOT its questions: since keel-cloud spec 048 the "
                                    "assumptions job writes no questionnaire, and the one "
                                    "QUESTIONS call that writes the project's one questionnaire "
                                    "fires on the *approval*, which this length deliberately "
                                    "never makes"
                                    if agent_host.short_reaches_the_assumptions(HOST) else
                                    "the plugin from the public marketplace, the skill seen as a "
                                    "plugin skill, a runtime awaiting approval, a code this Keel "
                                    "issued, the device approved, `already_connected`, the "
                                    "executor chosen by flag, the pin, and one confirmation card"),
                                "not run, and run weekly instead": (
                                    "the PROBLEM approval, SOLUTION, COMMERCIAL, the people, the "
                                    "reading, *What this says*, the overview and one card"),
                                "what it stops after": agent_host.short_stops_at(HOST),
                                "the framing took, by this harness's own clock": round(
                                    framing_took_s, 1),
                                "the founder this run typed as": founder.project_name,
                                "the entry they came from": entry.id})
        else:
            for stage in STAGES:
                _walk_stage_live(page, recorder, _get, project_id, stage, founder.statement(stage))
                # The ledger has moved exactly once at this point (spec 024 FR-006).
                if KEELS_AI and stage == STAGES[0]:
                    _the_number_went_down()
                ReviewCard(page, recorder, web_base).continue_onward()

            # **And now the founder waits for the questions** (spec 026; keel-cloud spec 048).
            # The third approval is what starts the `QUESTIONS` call that writes the project's one
            # questionnaire, and People is locked until it lands -- so this is both where a founder
            # actually waits and the only place the pick lists the review cards no longer carry can
            # be asserted. `_read_the_lines`'s own comment points here.
            _the_questions_land(page, recorder, _get, _post, project_id)

            people = People(page, recorder, web_base)
            people.open(project_id)
            with recorder.step("§1.4: People unlocks once the questions are written -- and every "
                                "framed card is still approved", party="founder",
                                kind="assert") as h:
                # **Two facts, in one step, because they are two different faults** (spec 026
                # FR-015/FR-016; keel-cloud spec 048 FR-028/FR-029; keel-web spec 026 FR-017).
                #
                # The sentence this step used to make -- *People unlocks once every framed card is
                # approved* -- was the whole rule until 048. It is now half of it: approving the
                # last card no longer makes the questions exist, so for a minute or two the three
                # cards are all approved and there is nothing anybody can be sent. keel-web stopped
                # recomputing the gate from the cards and reads `Overview.questionsState` instead
                # (`gateOpen = questionsState === "READY"`), which is the same gate
                # `Project.invite` enforces on the wire (`rule: "questionnaire"`, *"no questions
                # have been written for this project yet"*).
                #
                # So the referee reads it too, rather than becoming the one party in the system
                # computing it a fourth way -- and keeps the old reading beside it, because
                # *approved and still locked* and *unlocked while unapproved* are two different
                # faults and one assertion could not tell them apart. `_the_questions_land` above
                # has already waited for READY; what this adds is that the **screen** agrees.
                shell = Shell(page, recorder)
                locked = shell.people_locked()
                overview_body = _get(f"/v2/projects/{project_id}/overview") or {}
                approvals = {row.get("type"): row.get("approved")
                             for row in overview_body.get("stages") or []}
                unapproved = [stage for stage in STAGES if approvals.get(stage) is not True]
                h.record_assert({"people_locked": False, "questionsState": "READY",
                                  "approved": {stage: True for stage in STAGES}},
                                 {"people_locked": locked,
                                  # FR-017: keel-web's own sentence, so a failure says *Writing the
                                  # questions for your lines* or *We couldn't write the questions
                                  # for your lines* instead of `True`.
                                  "why, in keel-web's own words": (shell.people_locked_reason()
                                                                   if locked else None),
                                  "questionsState": overview_body.get("questionsState"),
                                  "approved": approvals})
                assert not unapproved, (
                    f"the journey reached People with {unapproved} unapproved; People unlocking "
                    f"here would mean keel-cloud let an invitation out before the lines were "
                    f"accepted")
                assert overview_body.get("questionsState") == "READY", (
                    f"the overview reads questionsState="
                    f"{overview_body.get('questionsState')!r} at the People page, having read "
                    f"READY a moment ago -- the questionnaire was rewritten or withdrawn between "
                    f"the two")
                assert not locked, (
                    f"People stayed locked with all three cards approved and the questions READY. "
                    f"keel-web says: {shell.people_locked_reason()!r}")

            # ---------------------------------- the deck, before anybody has answered anything
            # **The download's disabled state, and this is the only moment it can be read.**
            # keel-web spec 027 FR-025 state 3: while `Standing.people` holds no `READ`, *Download
            # the brief* is replaced by a control that is present, disabled and says why --
            # *Nothing to hand over yet*, with *The brief fills as your AI reads answers.* beside
            # it. Every stage is approved here, so the route renders the deck rather than the
            # walk's step; nobody has answered, so nothing has been read. One reading later the
            # state is gone for the rest of the project's life, which is the same reason
            # `_assert_no_paragraph_yet` reads the "not yet" note where it does.
            #
            # **This is where the assertion that used to read *What this says*' own "not yet" note
            # on this screen now stands.** keel-web spec 027 FR-020 took the paragraph off the
            # overview and FR-027 prints it on page 1 of the sheet, which prints no note at all
            # ("a sheet does not explain to itself why a block it left out is missing"). So the
            # founder-facing sentence for *there is nothing yet* is the download's own, and it is
            # asserted here beside the wire's note, which keel-cloud still composes.
            overview = Overview(page, recorder, web_base)
            overview.open(project_id)
            with recorder.step("§1.7: with every stage approved and nobody asked, the deck stands "
                                "and there is nothing to hand over yet",
                                party="founder", kind="assert") as h:
                wire = _get(f"/v2/projects/{project_id}/overview") or {}
                download = overview.download_state()
                h.record_assert({"deck": True, "download enabled": False,
                                  "label": "Nothing to hand over yet",
                                  "whatThisSays": None, "a note in its place": "non-empty"},
                                 {"deck": overview.is_deck(),
                                  "download": download,
                                  # The ship column, as keel-web **038** draws it: the worst
                                  # stage's own word, its tip, and the two tiles. `ship_caption()`
                                  # is recorded beside them and answers `''` -- FR-004 retired
                                  # `shipCaption`'s only caller, and a bundle that shows the empty
                                  # string is a bundle that shows which deploy it ran against.
                                  "headline": overview.headline(),
                                  "the tip under it": overview.headline_note(),
                                  "tiles": overview.tiles(),
                                  "ship caption, retired by 038 FR-004":
                                      overview.ship_caption(),
                                  "panels": [{"stage": q["stage"], "state": q["state"],
                                              "word": q["word"]}
                                             for q in overview.panels()],
                                  "whatThisSays": wire.get("whatThisSays"),
                                  "whatThisSaysNote": wire.get("whatThisSaysNote"),
                                  "on the overview, which no longer draws it":
                                      overview.carries_what_this_says()})
                assert overview.is_deck(), (
                    "every stage is approved and the overview is still drawing the walk's step; "
                    "the deck is what an approved project's overview is (keel-web spec 027)")
                assert download["label"].strip(), (
                    "the deck's foot offers no download control at all -- not a disabled one "
                    "either, which is the state keel-web FR-025 requires here")
                assert not download["enabled"], (
                    f"the download is live before a single answer has been read: {download!r}")
                assert download["why"].strip(), (
                    "the download is disabled and says nothing about why; a disabled control that "
                    "does not say why is a bug the founder has to guess at (design §6.1 "
                    "decision 5)")
                assert not overview.carries_what_this_says(), (
                    "the overview still draws a *What this says* block; keel-web spec 027 FR-020 "
                    "moved it to page 1 of the sheet and this screen is the deck now")
                assert wire.get("whatThisSays") is None, (
                    f"a paragraph exists before anything was read: {wire.get('whatThisSays')!r}")

            # Each of the chosen people gets their own link and answers in their own words, in
            # corpus order (the founder, 2026-09-13: five, so the brief has a verdict to say).
            answers = {}
            for one in people_chosen:
                url = _invite_one_live(page, recorder, project_id, web_base, one.person)
                answers[one.person] = _answer_whatever_is_asked(browser, recorder, url, one,
                                                                 entry)
            with recorder.step(f"spec 021 (amended 2026-09-13): {len(people_chosen)} people "
                                "invited and answered, each on their own link",
                                party="stack", kind="assert") as h:
                # The harness's own inputs, never the model's reading of them: every chosen
                # person was sent in and typed at least one story.
                h.record_assert({"people": people_names},
                                 {name: {"anchors answered": len(a["answered"]),
                                         "picks": len(a["picked"])}
                                  for name, a in answers.items()})
                assert list(answers) == people_names, (
                    f"invited {people_names}, answered {list(answers)}")
                assert all(a["answered"] for a in answers.values()), (
                    "a chosen person typed nothing anywhere")

            people.open(project_id)
            people.switch_to_who_tab()
            read_result = people.read_all_and_wait(timeout_s=420)
            with recorder.step("§1.6: the host read the answer, and the toast names what moved",
                                party="founder", kind="assert") as h:
                h.record_assert("a non-empty toast", read_result["toast_text"])
                assert read_result["toast_text"].strip(), (
                    "the reading produced no toast, so nothing was read")

            # ------------------------------------------------------------------------- §1.7a
            # **The fault matrix run 36895521843 actually showed, and nothing asserted** (spec 028
            # FR-020 … FR-022). That run read five answers and moved *"Seven things ... on the
            # problem card and four on your solution"* -- and nothing on the commercial. All five
            # COMMERCIAL lines came back `untested` with `peopleAnswered: 5`, because the stranger
            # had typed a filler sentence under the two anchors the corpus had no story for and
            # keel-cloud read it, correctly, as a guess. The journey then failed three steps later
            # on keel-web's panel for drawing no rows it had nothing to draw.
            #
            # This is the step that catches it where it happens -- at the readings, before any
            # screen -- and **names the party from the wire**. `GET /stages/{stage}` carries
            # `BeliefStanding.guessed` and `inside`/`outside` on every belief, which is the only
            # place the wire says whether the answers were read as occasions at all. Nothing here
            # is inferred: every number is a field keel-cloud sent (AGENTS.md's house rule).
            #
            # It stands **before** the deck deliberately. A stage with nothing standing is not a
            # screen bug, and the step that can blame this harness has to run before the steps
            # that blame the product.
            with recorder.step("§1.7a: every approved stage was tested by somebody -- no stage is "
                                "entirely untested after everyone answered",
                                party="stack", kind="assert") as h:
                standing_after = _get(f"/v2/projects/{project_id}/standing") or {}
                overview_after = _get(f"/v2/projects/{project_id}/overview") or {}
                stages_after = {row.get("type"): row
                                for row in overview_after.get("stages") or []}
                untested_faults, read_as = [], {}
                for stage in STAGES:
                    counted = _stage_lines(standing_after, stage)
                    summary = stages_after.get(stage) or {}
                    answered_by = summary.get("peopleAnswered")
                    anchoring = _stage_anchoring(
                        _get(f"/v2/projects/{project_id}/stages/{stage}") or {})
                    read_as[stage] = {
                        "the wire's own numbers": counted,
                        "peopleAnswered": answered_by,
                        "people invited by this run": len(people_chosen),
                        "how the answers were read, summed over this stage's beliefs": anchoring,
                    }
                    if not counted["total"]:
                        continue
                    if counted["untested"] != counted["total"]:
                        continue
                    if (answered_by or 0) < len(people_chosen):
                        # Fewer people answered than were invited: the stage having nothing is
                        # arithmetic, not a fault, and the people table is where that is read.
                        read_as[stage]["why this is not a fault"] = (
                            f"{answered_by} of {len(people_chosen)} answered")
                        continue
                    untested_faults.append(
                        f"{stage}: every one of its {counted['total']} lines is untested and "
                        f"{answered_by} people answered its occasion. Whose fault: "
                        f"{_whose_fault(anchoring)}")
                h.record_assert({"stages entirely untested after everyone answered": [],
                                  "people invited": len(people_chosen)},
                                 {"faults": untested_faults, "per stage": read_as})
                assert not untested_faults, (
                    "a stage the founder approved was tested by nobody, and five people "
                    f"answered: {untested_faults}")

            # --------------------------------------------------------------------------- §1.7
            # **The overview is the deck now** (keel-web spec 027 `brief-ship`, merged to master
            # `7e5a2a8` and deployed). What stood here until that deploy -- the evidence bar, the
            # four-word legend, the 207-word *What this says* paragraph and the three `.ocards`
            # cards -- is gone from this route, and matrix run 36870786241 died waiting thirty
            # seconds for `.ocards` on a screen that no longer draws it.
            #
            # Nothing below is deleted. The three assertions that stood here stand still, in the
            # place the thing they are about now stands:
            #
            # | what it asserted | where it stands now |
            # |---|---|
            # | the paragraph exists and is rendered verbatim | the sheet's page 1, under its own heading |
            # | three stage cards, each with a status | three panels, each naming its stage and its word |
            # | the legend's four words | **nowhere on this screen** -- the four counts are `GET /standing`'s own four lists, and the per-stage half is each panel's own count line, which is asserted against them |
            with recorder.step("§1.7: *What this says* -- the paragraph the host wrote, unasked",
                                party="founder", kind="assert") as h:
                # keel-cloud starts a BRIEF job by itself when a reading batch finishes
                # (`ReadingBatchService.sayWhatThisSays`), so the founder is given nothing to wait on
                # and this polls the wire the runtime is answering. On the Keel door this is the
                # scenario's other in-process job (spec 024 FR-010), so it gets the same ceiling
                # `KEELS_AI_JOB_WAIT_S` gives the review card, and the same fail-fast: the wire is
                # asked whether the door is shut on every poll rather than only after the deadline,
                # so a refunded BRIEF job is reported in seconds, not in the full ceiling.
                deadline = _now() + (KEELS_AI_JOB_WAIT_S if KEELS_AI else 420)
                paragraph = None
                while _now() < deadline:
                    wire = _get(f"/v2/projects/{project_id}/overview") or {}
                    paragraph = wire.get("whatThisSays")
                    if paragraph and paragraph.strip():
                        break
                    if KEELS_AI:
                        _refuse_if_the_door_is_shut(recorder, _get, project_id)
                    page.wait_for_timeout(3_000)
                # **The screen half of this assertion moved and did not loosen.** keel-web spec 027
                # FR-020 took the paragraph off the overview and FR-027 prints it on page 1 of the
                # sheet, verbatim, under `WHAT_THIS_SAYS_HEADING`. So the wire half is asserted
                # here, where the job is waited for, and the rendered-verbatim half is asserted on
                # the sheet below -- against `PrintPage.what_this_says_paragraph()`, which reads
                # page 1's own `p.pclaim` and not the stage pages' three claims.
                h.record_assert({"whatThisSays": "non-empty"},
                                 {"wire": paragraph,
                                  "where its screen half is asserted": (
                                      "page 1 of the brief, below -- the overview was asserted to "
                                      "draw no *What this says* block before the invites went out")})
                assert paragraph and paragraph.strip(), (
                    "no *What this says* paragraph after the reading -- the BRIEF job the host was "
                    "given never produced one")

            overview.open(project_id)
            overview_wire = _get(f"/v2/projects/{project_id}/overview") or {}
            standing_wire = _get(f"/v2/projects/{project_id}/standing") or {}
            by_stage = {row.get("type"): row for row in overview_wire.get("stages") or []}

            # **The deck is the board now** (keel-web spec `038-overview-board`, merged `4540aa3`
            # 2026-10-01 and live on staging; keel-cloud `canon/designs/overview-board-design.md`
            # §4). `runs/DRIFT.md` **#73** is what reading the old regions cost: every panel came
            # back `word: ""`, `claim: ""`, `parts: {}` on a board that was drawing *Will they pay
            # · both deal-breakers hold · 5 people answered* perfectly well, and the matrix's last
            # step was red on every cell that reached it -- a stale referee, not a product fault.
            # It was reached for the first time with five answers on run 37147770058; before that
            # #71's participant red had stopped every cell short of the readings, and the deck
            # with no reading at all passes.
            #
            # **Nothing below is deleted.** Three assertions lost their **subject** rather than
            # their selector, and each one says so where it stood, with the FR that removed it:
            #
            # | what it asserted | where it stands now |
            # |---|---|
            # | *Held* / *Did not hold*, three panels of two parts | **gone** (FR-009/FR-013) -- a card is a snapshot of deal-breakers, in three exhaustive states. The state rule, the cap of two and the tail at its own number are asserted in its place, against `GET /standing`'s own two lists |
            # | *N of M lines holding* in the count line | **the ship column's own tile** (FR-012/FR-025 -- `panelLinesHolding` lost its last caller; the card's foot is `panelDealBreakers · panelPeopleAnswered` alone). Asserted against `GET /standing`'s four lists summed, where the number now is |
            # | the worst panel is **open at rest**, with no tail on either part | **the headline word** (FR-001/FR-008/FR-011) -- a card does not expand, the whole card is a link to its stage page, and the worst stage's own word leads the ship column. `panel--worst` is asserted still, because the phone's CSS hoists off it (spec 027 FR-018) |
            #
            # And the one that only lost its selector is the one that went red: the status word is
            # in `span.panel__pill` now, not `span.panel__word` (FR-006), and it carries the word
            # **alone** -- never `statusWithDrift` (FR-007).
            with recorder.step("§1.7: the deck -- one band per stage, coloured by the verdict the "
                                "wire sent, and one panel per band saying it in words",
                                party="founder", kind="assert") as h:
                bands = overview.bands()
                panels = overview.panels()
                expected = {stage: _band_wash(by_stage.get(stage) or {}) for stage in STAGES}
                got_wash = {band["stage"]: band["wash"] for band in bands}
                got_word = {q["stage"]: q["word"] for q in panels}
                band_label = {band["stage"]: band["label"] for band in bands}
                by_panel = {q["stage"]: q for q in panels}
                h.record_assert({"bands": 3, "panels": 3, "wash by stage": expected,
                                  "every band names its stage and its word": True,
                                  "every card is a link to its own stage page": True},
                                 {"headline": overview.headline(),
                                  "tiles": overview.tiles(),
                                  "ship, in one line": overview.ship_label(),
                                  "bands": bands, "panels": panels,
                                  "wash the wire implies": expected,
                                  "the verdicts the wire sent": {
                                      stage: (by_stage.get(stage) or {}).get("verdict")
                                      for stage in STAGES}})
                assert len(bands) == 3, f"the ship drew {len(bands)} bands, not three: {bands}"
                assert len(panels) == 3, f"the deck drew {len(panels)} panels, not three: {panels}"
                assert set(got_wash) == set(STAGES), (
                    f"the bands name {sorted(got_wash)}; a band is one stage and there are three")
                assert set(got_word) == set(STAGES), (
                    f"the panels name {sorted(got_word)}; a panel is one stage and there are three")
                # **Colour is never the only carrier** (keel-web spec 027 FR-003/SC-005, and 038
                # FR-006 keeps it): every band's own verdict is a word within 8px of it, and the
                # figure says all three in one line. So the word is asserted as well as the wash,
                # and a board that lost every colour would still pass this step. **The word moved
                # into the pill and did not go** -- which is the whole of DRIFT #73.
                wordless = [stage for stage, word in got_word.items() if not (word or "").strip()]
                assert not wordless, (
                    f"a panel carries no status word at all: {wordless} -- colour would be the "
                    f"only carrier of those verdicts")
                nameless = [q["stage"] for q in panels if not (q["name"] or "").strip()]
                assert not nameless, f"a panel does not name its own stage: {nameless}"
                # **The pill carries the status word alone** (FR-007): `measuredStatus(verdict)
                # .label`, never `statusWithDrift`. Measured by keel-web, *Not holding up · smaller
                # than you think* wraps the head on every failing card, and the drift clause is the
                # nuance *"remember this is a snapshot"* argues against -- it is not deleted from
                # the product, the stage page and the printed sheet keep it. So the pill's word is
                # asserted to be one of the five `measuredStatus` can say and to carry no clause.
                drifting = {stage: word for stage, word in got_word.items()
                            if word.strip().casefold() not in Overview.STATUS_WORDS}
                assert not drifting, (
                    f"a card's pill says something other than the five words `measuredStatus` has: "
                    f"{drifting}. The pill carries the status word **alone** (keel-web 038 FR-007) "
                    f"-- a drift clause in it is the head wrapping on every failing card, and a "
                    f"sentence in it is a word a model wrote")
                # **Two carriers, one verdict.** The band's own `aria-label` is *The problem —
                # People disagree*, read off a different node by a different reader; the pill is
                # read off the card. Comparing them is how the referee says *the screen agrees with
                # itself* without holding a copy of keel-web's own strings: the band may append a
                # drift clause and the pill may not, so the pill's word has to be inside the band's
                # label, not equal to it.
                disagreeing = {stage: {"the pill": got_word[stage],
                                        "the band's own label": band_label.get(stage, "")}
                                for stage in STAGES
                                if got_word[stage].strip().casefold()
                                not in (band_label.get(stage) or "").casefold()}
                assert not disagreeing, (
                    f"a card's pill and its own band say different verdicts: {disagreeing}. Both "
                    f"are `measuredStatus` on the verdict the wire sent, read off two nodes; a "
                    f"screen that disagrees with itself is drawing one of them from something else")
                # The tone is the one class a scenario can put against the verdict the wire sent,
                # and on the board it is `panel__pill--<tone>` (FR-006) where it was `st-*`.
                mistoned = {stage: {"the pill's tone": by_panel[stage]["tone"],
                                     "the wash the wire implies": expected[stage]}
                             for stage in STAGES if by_panel[stage]["tone"] != expected[stage]}
                assert not mistoned, (
                    f"a card's pill is tinted for a verdict the wire did not send: {mistoned}")
                wrong = {stage: {"wash": got_wash[stage], "the wire's verdict":
                                  (by_stage.get(stage) or {}).get("verdict"),
                                  "expected": expected[stage]}
                          for stage in STAGES if got_wash[stage] != expected[stage]}
                assert not wrong, (
                    f"a band is coloured for a verdict the wire did not send: {wrong}. Position "
                    f"means stage and colour means verdict (keel-web FR-002); a band that "
                    f"disagrees with `GET /overview` is the deck inventing a verdict.")
                # **FR-008: the whole card is the link** to `/p/{id}/s/{stage}`, and nothing inside
                # it is a second control -- which is what makes the tail a count that navigates
                # rather than the in-place expander the founder struck on 2026-09-30. `href` and
                # not a click: following it is the stage page's own business.
                undoored = {stage: by_panel[stage]["href"] for stage in STAGES
                            if not (by_panel[stage]["href"] or "").endswith(
                                f"/p/{project_id}/s/{stage}")}
                assert not undoored, (
                    f"a card is not a link to its own stage page: {undoored}. The whole card is "
                    f"the door (keel-web 038 FR-008), and it is the only one the body has now "
                    f"that the rows carry no control of their own")

            with recorder.step("§1.7: each card is in exactly one of 038's three states, and its "
                                "rows, its cap and its foot are that state's own rule",
                                party="founder", kind="assert") as h:
                # **Every number compared, never recomputed.** The state is `dealBreakersHolding`
                # against `dealBreakersTotal` and the verdict, all three `StageSummary`'s own; the
                # rows are `GET /standing`'s `notHoldingUp` then `peopleDisagree`, filtered to the
                # stage and to `LOAD_BEARING`, in the wire's own order; the foot's two clauses are
                # the deal-breaker pair and `peopleAnswered`. The referee does the same filter the
                # screen does and compares the two; it computes no verdict and no median
                # (AGENTS.md's house rule).
                #
                # **Two assertions stood here and have lost their subject** -- written here rather
                # than deleted, with the FR that removed each:
                #
                # - *N of M lines holding* in the count line. **Gone** (keel-web 038
                #   FR-012/FR-025): the card's foot is `panelDealBreakers · panelPeopleAnswered`
                #   alone, and `panelLinesHolding` lost its last caller on this screen -- *"a
                #   snapshot of deal-breakers has no use for a count of every line"*. The number
                #   itself did not go: it is the ship column's own `lines` tile (FR-003), and the
                #   step below asserts it there against the same four lists.
                # - *the panel accounts for every tested line and no others* (`_panel_accounting`,
                #   spec 028 FR-018/FR-019). **Gone** (FR-009/FR-013): a card has no *Held* list,
                #   no worth-knowing line and no failing deal-breaker past the second, so there is
                #   no sum on the screen to put against the wire's. What stands in its place is
                #   stricter about what the card *does* promise -- the state rule, the cap of two,
                #   the tail at its own number, and the foot drawn in exactly two of the three
                #   states.
                #
                #   **And the assertion that used to stand here is gone for cause twice over now**
                #   (spec 028 FR-018/FR-019, kept verbatim because a record of a move is the half
                #   that survives deletion). The first version read `counted["total"] and not
                #   (held or failed)` -- *this stage has lines and the panel shows none of them* --
                #   and matrix run 36895521843 is what that cost: `COMMERCIAL` had five lines,
                #   every one of them `untested`, and a panel had two parts and no third, so there
                #   was nothing for it to draw and it correctly drew nothing. The referee failed
                #   keel-web for obeying keel-web's own spec, and named the wrong repository, which
                #   is the worst thing a referee can do. Its replacement, the accounting above, is
                #   what keel-web 038 then took the subject of. An all-untested stage is state C
                #   here, which the state rule reads directly -- and the fault the red run actually
                #   showed is §1.7a's, above, where the readings are.
                panels = {q["stage"]: q for q in overview.panels()}
                faults = []
                reported = {}
                for stage in STAGES:
                    panel = panels.get(stage)
                    summary = by_stage.get(stage) or {}
                    failed = _stage_deal_breakers(standing_wire, stage)
                    want = _expected_card(summary, failed)
                    state = Overview.state_of(panel or {})
                    rows = Overview.rows_of(panel or {})
                    fails = Overview.fails_of(panel or {})
                    tail = Overview.card_tail(panel or {})
                    foot = ((panel or {}).get("count") or "").strip()
                    reported[stage] = {
                        "data-state": state, "the state the wire's numbers make": want["state"],
                        "rows": [{"tone": row["tone"], "box": row["box"],
                                   "heading": row["heading"], "text": row["text"]}
                                  for row in rows],
                        "tail": tail, "foot": foot,
                        "the wire's own numbers": _stage_lines(standing_wire, stage),
                        "the rule, from the wire": want,
                    }
                    if panel is None:
                        faults.append(f"{stage}: no card at all")
                        continue
                    if state not in Overview.CARD_STATES:
                        faults.append(
                            f"{stage}: the card carries `data-state={state!r}`; keel-web 038 "
                            f"FR-009 draws one of {list(Overview.CARD_STATES)} and the three are "
                            f"exhaustive and disjoint")
                        continue
                    if state != want["state"]:
                        faults.append(
                            f"{stage}: the card is in state {state}; the wire's own numbers "
                            f"(verdict {summary.get('verdict')!r}, deal-breakers "
                            f"{want['deal-breakers, on the wire']}) make it {want['state']}")
                    if len(rows) != want["rows"]:
                        faults.append(
                            f"{stage}: state {state} drew {len(rows)} rows and its rule draws "
                            f"{want['rows']} -- {[row['text'] for row in rows]}")
                    answered = summary.get("peopleAnswered")
                    if answered is None:
                        faults.append(f"{stage}: the wire reports no `peopleAnswered`")
                    # ---- state C: one grey row, and **no foot** -- this row *is* the count.
                    if state == "C" and rows:
                        text = rows[0]["text"]
                        if rows[0]["box"] != "wait":
                            faults.append(f"{stage}: state C's row is not the grey one: "
                                           f"{rows[0]!r}")
                        if answered is not None and not re.search(
                                rf"\b{answered}\b\s+(person|people)\s+answered", text):
                            faults.append(f"{stage}: state C's row reads {text!r}; the wire says "
                                           f"{answered} answered")
                        if f"{VERDICT_PEOPLE_FLOOR} needed" not in text:
                            faults.append(
                                f"{stage}: state C's row reads {text!r} and never says the floor. "
                                f"`panelAnsweredOfFloor` is the one place on this screen the "
                                f"verdict rule's own five is spelled out, and a founder below it "
                                f"is owed the number (keel-web 038 FR-009)")
                    # ---- state A: one green row, *No major blockers* -- or none at all where the
                    # stage carries no deal-breaker, which is FR-012's own edge case: *No major
                    # blockers* would be true but hollow, so the foot's *N people answered* stands
                    # alone rather than dressing an absence up as an all-clear.
                    if state == "A" and rows:
                        if rows[0]["box"] != "ok":
                            faults.append(f"{stage}: state A's row is not the green one: "
                                           f"{rows[0]!r}")
                        if not rows[0]["text"]:
                            faults.append(f"{stage}: state A drew an empty row")
                    # ---- state B: the two worst failing deal-breakers, `CONTRADICTED` before
                    # `MIXED`, each one `beliefHeading` **alone** with its own glyph -- and the
                    # glyph is the only carrier left of which of the two it is (design §5.7).
                    if state == "B":
                        if not rows:
                            faults.append(
                                f"{stage}: state B drew no row at all. A stage's verdict is the "
                                f"worst among its applying load-bearing beliefs, so a MIXED stage "
                                f"must carry a MIXED deal-breaker -- an empty red block is "
                                f"unreachable (keel-web 038 SC-003)")
                        if len(fails) > Overview.ROW_CAP:
                            faults.append(
                                f"{stage}: {len(fails)} failing rows on the card; the founder's "
                                f"own cap is {Overview.ROW_CAP} and the rest are the tail "
                                f"(FR-009/FR-011)")
                        got_headings = [row["heading"] for row in fails]
                        if got_headings != want["the two the cap shows"]:
                            faults.append(
                                f"{stage}: the card's rows are {got_headings}; `GET /standing`'s "
                                f"own two lists, filtered to this stage's deal-breakers and in "
                                f"the wire's order, make them {want['the two the cap shows']} "
                                f"(FR-010 -- notHoldingUp before peopleDisagree, so the two shown "
                                f"are the two worst)")
                        got_tones = [row["tone"] for row in fails]
                        if got_tones != want["their own glyphs"]:
                            faults.append(
                                f"{stage}: the rows' glyphs are {got_tones} and the wire's "
                                f"verdicts make them {want['their own glyphs']} -- ✕ for "
                                f"CONTRADICTED, ! for MIXED, and the glyph is the only carrier "
                                f"left of which it is")
                    # ---- the tail: *+N more ›*, present only where more than the cap failed, and
                    # at the number the wire's own lists make. **It is not the expander the founder
                    # struck on 2026-09-30** (FR-011): it opens nothing, holds nothing, fetches
                    # nothing and moves nothing -- it is text inside the card's own link, which is
                    # why `open_every_tail()` has no subject on this screen.
                    if want["tail"] and not tail:
                        faults.append(
                            f"{stage}: {len(failed)} deal-breakers failed and the card shows "
                            f"{len(fails)} with no tail. Nothing is lost to the cap only because "
                            f"the tail says how many more (FR-011)")
                    elif tail and not want["tail"]:
                        faults.append(
                            f"{stage}: the card carries the tail {tail!r} and the wire has "
                            f"{len(failed)} failing deal-breakers, which the cap of "
                            f"{Overview.ROW_CAP} does not exceed")
                    elif tail and _tail_number(tail) != want["tail"]:
                        faults.append(
                            f"{stage}: the tail reads {tail!r}; {len(failed)} failed and "
                            f"{len(fails)} are shown, so it is {want['tail']} more")
                    # ---- the foot: `panelDealBreakers · panelPeopleAnswered`, in states A and B
                    # and **not** in C (FR-009/FR-012). It is the only per-stage people count left
                    # on the board and the only thing that supplies the denominator the rows and
                    # the tail cannot.
                    if want["foot"] and not foot:
                        faults.append(
                            f"{stage}: state {state} draws no foot. It is the only per-stage "
                            f"people count left on the board and the rows' own denominator "
                            f"(FR-012)")
                    if not want["foot"] and foot:
                        faults.append(
                            f"{stage}: state C drew the foot {foot!r} as well as its count row. "
                            f"The row *is* the count there, and saying it twice is the repetition "
                            f"FR-009 took out")
                    if foot:
                        if answered is not None and not re.search(
                                rf"\b{answered}\b\s+(person|people)\s+answered", foot):
                            faults.append(f"{stage}: the foot reads {foot!r}; the wire says "
                                           f"{answered} answered")
                        total = summary.get("dealBreakersTotal") or 0
                        if total and "deal-breaker" not in foot:
                            faults.append(f"{stage}: {total} deal-breakers on the wire and no "
                                           f"deal-breaker clause in {foot!r}")
                        if not total and "deal-breaker" in foot:
                            faults.append(f"{stage}: no deal-breaker on the wire and the foot "
                                           f"says {foot!r} -- *0 of 0* is what keel-web's own "
                                           f"edge case forbids")
                h.record_assert({"faults": [],
                                  "each card": "in the state the wire's own numbers make it, with "
                                               "that state's own rows, cap, tail and foot"},
                                 {"faults": faults, "per stage": reported})
                assert not faults, f"a card and the wire disagree: {faults}"

            with recorder.step("§1.7: the ship column leads with the worst stage's own word, and "
                                "its two tiles are the wire's own counts",
                                party="founder", kind="assert") as h:
                # **This is where *the worst panel is open at rest* stands now.** keel-web spec 027
                # FR-016 marked the worst stage's panel and opened it; spec 038 FR-008 made the
                # whole card a link and FR-011 made the tail a count, so **no card expands and
                # there is nothing to be open**. The subject of that assertion -- *a founder is
                # shown the worst stage first, without hunting for it* -- moved up the page into
                # FR-001's headline word: `measuredStatus(worstStage(overview.stages)).label`,
                # bare, 22 px serif, in that stage's own tone. `panel--worst` is asserted still,
                # because the phone's CSS hoists the worst card off exactly that marker (spec 027
                # FR-018, shipped by specs 028/029), so the marker has a live job even though
                # *open at rest* no longer does.
                #
                # The referee orders the verdicts the wire sent; it decides none. Worst is
                # `CONTRADICTED` → `MIXED` → `UNTESTED` → `SUPPORTED`, a tie going to the
                # **deepest band** -- problem, then solution, then price, on the design's own
                # argument that a ship is laid down keel-first and the keel is the part whose
                # failure capsizes the rest.
                marked = overview.worst_panel()
                want = _worst_stage(by_stage)
                worst_summary = by_stage.get(want) or {}
                headline = overview.headline()
                note = overview.headline_note()
                tiles = overview.tiles()
                worst_card = overview.panel(want) or {}
                # FR-002: `TIP_TOO_FEW_TO_CALL` stands under the headline **only** while the
                # headline reads *Too few to call*, which is `UNTESTED` with somebody having
                # answered -- both of them fields the wire sent. The slot is empty in every other
                # state, by design: the other three tips are written about one belief and are false
                # about a project, and there is no shipped sentence that is true of a project in a
                # good state.
                too_few = ((worst_summary.get("verdict") or "").upper() not in _WASH_OF_VERDICT
                           and (worst_summary.get("peopleAnswered") or 0) > 0)
                # FR-003: `N` *lines* from `Standing`'s four lists summed, and `N` *people asked*
                # from `standing.people.length`. **Two, not three** -- the market tile duplicates
                # the brand row. This is the tile the count line's *N of M lines holding* became.
                lines_on_wire = sum(len(standing_wire.get(key) or [])
                                    for key in ("holdingUp", "notHoldingUp", "peopleDisagree",
                                                "untested"))
                asked_on_wire = len(standing_wire.get("people") or [])
                def of_label(needle: str):
                    """The tile by its own label, never by position -- `STAT_LABEL_LINES` is
                    *lines* and `STAT_LABEL_PEOPLE` is *people asked*, and a reordering of the two
                    is not a fault this step is about."""
                    return next((tile for tile in tiles
                                 if needle in tile["label"].casefold()), None)

                lines_tile, asked_tile = of_label("line"), of_label("asked")
                h.record_assert({"panel--worst": want,
                                  "the headline word": "the worst stage's own",
                                  "the tip under it": "only while it reads *Too few to call*",
                                  "tiles": [lines_on_wire, asked_on_wire]},
                                 {"panel--worst": marked, "the wire's worst": want,
                                  "the verdicts the wire sent": {
                                      stage: (by_stage.get(stage) or {}).get("verdict")
                                      for stage in STAGES},
                                  "headline": headline,
                                  "the worst card's own pill": worst_card.get("word"),
                                  "the tone the wire implies": _status_tone(worst_summary),
                                  "the tip under it": note,
                                  "is it *Too few to call*, from the wire": too_few,
                                  "tiles": tiles,
                                  "the wire's own counts": {"lines": lines_on_wire,
                                                             "people asked": asked_on_wire}})
                assert marked == want, (
                    f"keel-web marked {marked!r} the worst panel; the verdicts the wire sent make "
                    f"it {want!r}. It is the card the phone hoists to the top of the column "
                    f"(keel-web spec 027 FR-018), and the stage the headline word speaks for.")
                assert headline["word"], (
                    "the ship column carries no headline word at all (`p.overall`). It is the one "
                    "word the whole board leads with (keel-web 038 FR-001), and without it a "
                    "founder has to read three cards to learn where the project stands")
                # **The screen agrees with itself, and the referee holds no copy of keel-web's own
                # strings.** The headline and the worst card's pill are both
                # `measuredStatus(that stage's verdict)`, read off two nodes by two readers.
                assert headline["word"].strip().casefold() == (
                        worst_card.get("word") or "").strip().casefold(), (
                    f"the headline reads {headline['word']!r} and the worst stage's own card says "
                    f"{worst_card.get('word')!r}. Both are `measuredStatus` on the verdict the "
                    f"wire sent for {want}; a board that disagrees with itself is drawing one of "
                    f"them from something else (keel-web 038 FR-001)")
                assert headline["tone"] == _status_tone(worst_summary), (
                    f"the headline is toned {headline['tone']!r} and the wire's verdict for {want}"
                    f" ({worst_summary.get('verdict')!r}) makes it "
                    f"{_status_tone(worst_summary)!r}. The word is in the worst stage's own tone "
                    f"(FR-001), unwashed -- `mute` where a band would be `none`")
                assert bool(note) == too_few, (
                    f"the tip under the headline is {note!r} and the headline reads "
                    f"{headline['word']!r}. keel-web 038 FR-002 draws `TIP_TOO_FEW_TO_CALL` there "
                    f"**only** while the project is too few to call, and leaves the slot empty "
                    f"otherwise -- the other three tips are written about one belief and are false "
                    f"about a project")
                assert len(tiles) == 2, (
                    f"the ship column drew {len(tiles)} stat tiles, not two: {tiles}. Two is the "
                    f"founder's own answer to design open question 6 -- the market tile the mock "
                    f"draws duplicates the brand row (FR-003)")
                assert lines_tile and lines_tile["value"] == lines_on_wire, (
                    f"the lines tile reads {lines_tile!r}; `GET /standing`'s four lists hold "
                    f"{lines_on_wire} lines. **This is where the count line's *N of M lines "
                    f"holding* went** (FR-003, FR-012/FR-025): the number is the ship column's "
                    f"now, and it is still the wire's own")
                assert asked_tile and asked_tile["value"] == asked_on_wire, (
                    f"the people tile reads {asked_tile!r}; `Standing.people` holds "
                    f"{asked_on_wire}. The label keeps the word *asked*: a person invited is not a "
                    f"person who answered (FR-003, P4)")

            with recorder.step("§1.7: now a reading exists, *Download the brief* is live",
                                party="founder", kind="assert") as h:
                # The other side of the disabled control asserted before the invites went out
                # (keel-web FR-025 states 1 and 3). `href` and not a click, because the control is
                # `target="_blank"` and following it is the next step's own business.
                download = overview.download_state()
                read = [p for p in (standing_wire.get("people") or [])
                        if (p.get("status") or "").upper() == "READ"]
                h.record_assert({"enabled": True, "href": f"/p/{project_id}/print"},
                                 {"download": download, "answers read, on the wire": len(read)})
                assert read, (
                    "the wire reports no READ answer after the reading, so the download has "
                    "nothing to be live for and this step is measuring the wrong thing")
                assert download["enabled"], (
                    f"the download is still disabled with {len(read)} answers read: {download!r}")
                assert (download["href"] or "").endswith(f"/p/{project_id}/print"), (
                    f"the download points at {download['href']!r}, not at this project's sheet")

            # ------------------------------------------------- §1.7, the brief the founder hands over
            # **In this same context, by URL, with `window.print` stubbed** -- `PrintRoute` raises
            # the dialog as soon as its five reads land, and no Playwright locator can dismiss a
            # native one. The founder's own door is the `target="_blank"` link asserted above;
            # `Overview.download()` follows it and answers the popup, and the journey does not
            # spend a second tab to prove a link it has already read.
            print_page = PrintPage(page, recorder, web_base)
            print_page.open(project_id)
            with recorder.step("§1.7: the brief is five pages, and page 1 carries the paragraph "
                                "under its own heading and the 16:9 block",
                                party="founder", kind="assert") as h:
                one = print_page.page_one()
                block = print_page.block_169()
                printed = print_page.what_this_says_paragraph()
                h.record_assert({"pages": 5, "whatThisSays": "rendered verbatim",
                                  "16:9 block": {"bands": 3, "panels": 3, "caption": "present"}},
                                 {"pages": print_page.page_count(), "page 1": one,
                                  "16:9": block,
                                  "the heading above it": print_page.what_this_says_heading(),
                                  "the wire's own paragraph": paragraph})
                assert print_page.page_count() == 5, (
                    f"the brief is {print_page.page_count()} pages; keel-web spec 027 FR-024/FR-030 "
                    f"make it five -- page 1, one page a stage, and the evidence")
                assert not print_page.has_founder_chrome(), (
                    "the sheet rendered the founder's own chrome; it is its own page")
                assert founder.project_name in one["name"], (
                    f"page 1 is headed {one['name']!r}, not {founder.project_name!r}")
                assert print_page.what_this_says_heading().strip(), (
                    "page 1 prints a paragraph under no heading -- `WHAT_THIS_SAYS_HEADING` is "
                    "what tells a reader what the paragraph is")
                # **The assertion that stood on the overview, unchanged, on the page that draws it
                # now**: the server's own words, character for character. Comparing loosely is how
                # six green runs said nothing about the paragraph at all.
                assert printed == paragraph, (
                    f"page 1 prints {printed!r}, not the server's own {paragraph!r}")
                assert block["present"], (
                    "page 1 drew no 16:9 block; FR-026 makes it the thing a founder lifts straight "
                    "into a deck, and it is the same `ShipFigure` at a different size")
                assert len(block["bands"]) == 3 and len(block["panels"]) == 3, block
                assert block["caption"].strip(), (
                    "the 16:9 block carries no caption, so nothing on the sheet says what it is for")

            with recorder.step("§1.7: the evidence page counts every line and names nobody",
                                party="founder", kind="assert") as h:
                # keel-web FR-029 / SC-009, and the principle is **P8** -- a stranger's words held
                # on their terms. This is the page most likely to be forwarded to an agency or an
                # investor, and a table of names is a list that travels. The named quotes stay on
                # the stage pages, where a founder can check them, and that is asserted too.
                evidence = print_page.evidence_page()
                people_on_the_wire = [str(p.get("personName") or "")
                                      for p in (standing_wire.get("people") or [])]
                lines_total = sum(_stage_lines(standing_wire, stage)["total"] for stage in STAGES)
                cells = " ".join(cell for row in evidence["rows"] for cell in row)
                leaked = sorted({name for name in people_on_the_wire
                                  if name.strip() and name in cells})
                h.record_assert({"rows": lines_total, "names on page 5": [],
                                  "columns": list(PrintPage.EVIDENCE_COLUMNS)},
                                 {"rows": len(evidence["rows"]), "columns": evidence["columns"],
                                  "heading": evidence["heading"], "lede": evidence["lede"],
                                  "names on page 5": leaked,
                                  "the people the wire names": people_on_the_wire,
                                  "named quotes, on the stage pages where they belong":
                                      print_page.quotes()[:3]})
                assert evidence["heading"].strip(), "the evidence page carries no heading"
                assert len(evidence["rows"]) == lines_total, (
                    f"the evidence page draws {len(evidence['rows'])} rows for the "
                    f"{lines_total} lines `GET /standing` carries -- every line, or it is not the "
                    f"evidence")
                assert not leaked, (
                    f"page 5 names {leaked}. Principle P8: this is the page that gets forwarded, "
                    f"and keel-web FR-029 puts no participant name on it.")
                assert not evidence["names"], (
                    f"page 5 drew an *In their words* block with names in it: {evidence['names']}")

            opened = OpenedCard(page, recorder, web_base)
            opened.open(project_id, "PROBLEM")
            with recorder.step("§1.7: one card, opened -- strips, numbers and a status on each",
                                party="founder", kind="assert") as h:
                strips = opened.strips()
                h.record_assert({"strips": ">= 1, each with a number and a status"},
                                 {"strips": len(strips), "first": (strips[0] if strips else None)})
                assert strips, "the opened PROBLEM card rendered no strips"
                for strip in strips:
                    assert str(strip.get("number") or "").strip(), f"an unnumbered strip: {strip!r}"

        # ------------------------------------------------- what it cost, and what never happened
        # **A QUESTIONS retry shows up here, and that is the design** (spec 026 FR-020). The one
        # retry `_the_questions_land` is allowed to spend does not remove the attempt it retried
        # from this list, so a journey whose questions failed once and then landed is a journey with
        # a failed job in it and this step names it. Deliberate, and the same posture
        # `_land_the_card`'s three benign follow-ups already take: the run goes on so that People,
        # the readings and the brief are all in the bundle as evidence, and the accounting at the
        # end says what failed. What the retry buys is that the failure was reported **where it
        # happened, in keel-cloud's own words**, instead of as a 420-second silence.
        with recorder.step("leg two: zero refusals, every job COMPLETED",
                            party="stack", kind="assert") as h:
            interactions = context.request.get(
                f"{cloud_base}/v2/inference-interactions?project_id={project_id}",
                timeout=20_000).json()
            refused = [{"interaction_id": i.get("interaction_id"), "screen": i.get("screen"),
                        "status": i.get("status"), "detail": i.get("detail"),
                        "diagnostic": i.get("diagnostic")}
                       for i in interactions if i.get("status") in REFUSED]
            unsettled = [{"interaction_id": i.get("interaction_id"), "screen": i.get("screen"),
                          "status": i.get("status")}
                         for i in interactions if i.get("status") not in SETTLED]
            bad_jobs = [{"job_id": (i.get("job") or {}).get("job_id"), "screen": i.get("screen"),
                         "status": (i.get("job") or {}).get("status"),
                         "error": (i.get("job") or {}).get("error")}
                        for i in interactions
                        if i.get("job") and (i.get("job") or {}).get("status") != "COMPLETED"]
            h.record_assert({"refusals": [], "jobs not COMPLETED": []},
                             {"interactions": len(interactions), "refusals": refused,
                              "not settled": unsettled, "jobs not COMPLETED": bad_jobs,
                              "statuses": sorted({i.get("status") for i in interactions})})
            assert not refused, f"the host's work was refused: {refused}"
            assert not bad_jobs, f"a job did not complete: {bad_jobs}"
            assert not unsettled, f"an interaction never settled: {unsettled}"

        if KEELS_AI:
            # ------------------------------------- what Keel's own AI did, and what it cost Keel
            # **Read off keel-cloud's own `execution` report, because there is no runtime home to
            # read.** On the three CLI doors the second, independent proof of who did the thinking
            # is `<KEEL_HOME>/jobs/*/envelope.json`, written by the process that ran the job. No
            # such process exists here, and the equivalent document is the `execution` block
            # keel-cloud's own executor settles each job with (keel-cloud spec 045 FR-043): written
            # by the executor, not by the founder, not by the model, and not by this harness.
            #
            # It is not a weaker reading; on this door it is the only one, and the *absence* of
            # the other is asserted rather than assumed -- see the empty `KEEL_HOME` below, which
            # is what makes "nothing else could have written this" a measurement.
            with recorder.step("spec 024: every job was answered by Keel's own AI, and every one "
                                "of them cost something", party="stack", kind="assert") as h:
                # **Each job's own detail, never the interaction list's stub.** `InteractionView.job`
                # carries `{job_id, turn_number, status, outcome, error}` and no `execution` at all
                # (keel-cloud `canon/openapi-v2.yaml`), so reading it here answered `None` to every
                # question and `cost_reported` False -- a well-formed wrong answer, which is the
                # worst shape a reading can have. Matrix run 36643795391 failed on exactly that,
                # with keel-cloud's own log showing both jobs settled `host=api` with a cost.
                per_job = keels_ai.jobs_with_their_execution(_get, interactions)
                door_jobs[:] = per_job
                wrong_host = [r for r in per_job if r["host"] != EXPECTED_EXECUTOR]
                costless = [r for r in per_job
                            if not r["cost_reported"] or (r["actual_cost_micro_usd"] or 0) <= 0]
                spent_micro = sum(r["actual_cost_micro_usd"] or 0 for r in per_job)
                h.record_assert({"execution.host": EXPECTED_EXECUTOR,
                                  "actual_cost_micro_usd": "present and > 0 on every job"},
                                 {"jobs": len(per_job), "per job": per_job,
                                  "jobs not answered by Keel's AI": wrong_host,
                                  "jobs with no cost reported": costless,
                                  "what this journey cost Keel, in micro-dollars": spent_micro,
                                  "...in dollars": round(spent_micro / 1_000_000, 4),
                                  "what the design expects": (
                                      "a five-participant journey is 1,250 credits ($12.50 at "
                                      "list) and about $2.44 of Keel's own inference "
                                      "(ai-credits-design.md §6.3)"),
                                  "models, recorded and asserted against nothing": sorted(
                                      {(r["model_requested"], r["model_used"]) for r in per_job})})
                assert per_job, "keel-cloud reported no jobs at all for this project"
                assert not wrong_host, (
                    f"a job of this project was not answered by Keel's AI: {wrong_host}. "
                    f"`execution.host` must read {EXPECTED_EXECUTOR!r} on this door (keel-cloud "
                    f"spec 045 FR-043) -- `claude`, `copilot` or `codex` there would mean a "
                    f"runtime answered a founder who has none.")
                assert not costless, (
                    f"a settled job carries no actual cost: {costless}. Invariant X6 -- *every "
                    f"settled job records its actual cost beside its price* -- is the one thing "
                    f"keel-cloud spec 045 exists to deliver, and a cell that passed on a null "
                    f"would be certifying it unmet. (Zero is not a pass either: spec 045 FR-027 "
                    f"makes zero mean the job failed before a call was made.)")

            with recorder.step("spec 024: nothing ever started a process -- this run's KEEL_HOME "
                                "is as empty as it was before the first screen",
                                party="stack", kind="assert") as h:
                leftovers = sorted(q.name for q in keel_home.iterdir()) if keel_home.is_dir() else []
                h.record_assert({"KEEL_HOME contents": [], "heartbeat": None,
                                  "launch log": "", "subprocesses run by the harness": 0},
                                 {"KEEL_HOME": str(keel_home), "contents": leftovers,
                                  "heartbeat": agent_host.read_heartbeat(keel_home),
                                  "launch log": agent_host.read_launch_log(keel_home)[:400],
                                  "subprocesses run by the harness": host.subprocesses_run,
                                  "agent, on the wire": (_me().get("agent") or {})})
                assert not leftovers, (
                    f"this run's KEEL_HOME is not empty: {leftovers}. On the Keel door nothing "
                    f"installs, nothing connects and nothing runs, so anything in here was "
                    f"written by something that should not exist.")
                assert agent_host.read_heartbeat(keel_home) is None
                assert host.subprocesses_run == 0, (
                    f"the Keel door ran {host.subprocesses_run} subprocess(es); it is supposed to "
                    f"run none, ever")
                assert not (_me().get("agent") or {}).get("connected"), (
                    "an agent is connected to a founder who never installed one")

            spend = {"door": "Keel's own AI, on Keel's own Anthropic account",
                     "people": len(people_chosen),
                     "credits at sign-up": agent_host.KEELS_AI_GRANT,
                     "credits before the first framing": credits_before,
                     "credits after the first framing": credits_after_first_job,
                     "credits now": _credits_now(),
                     "credits spent by this journey": (
                         None if credits_before is None or _credits_now() is None
                         else credits_before - _credits_now()),
                     "what the design expects a five-participant journey to cost": (
                         "1,250 credits -- 540 framing + 45 readings + 105 brief + 560 "
                         "conversation (ai-credits-design.md §6.3) -- which is $12.50 at list "
                         "price and about $2.44 of Keel's own inference"),
                     "what Keel actually paid, in micro-dollars": sum(
                         r["actual_cost_micro_usd"] or 0 for r in per_job),
                     "per job": per_job,
                     "jobs": len(per_job)}
            (run_dir / "spend.json").write_text(json.dumps({"host": HOST, **spend}, indent=2) + "\n")
            print(f"\nS-012 {LEGS} journey through Keel's own AI as {founder.project_name!r} "
                  f"({entry.id}): {len(per_job)} jobs; "
                  f"{spend['credits spent by this journey']} credits; "
                  f"{spend['what Keel actually paid, in micro-dollars']} micro-dollars of "
                  f"Keel's own inference")

            with recorder.step("spec 024: there is no way out to take -- there was never a "
                                "runtime", party="stack", kind="note") as h:
                h.record_wire(None, {
                    "not run": "keel-connect-skill's `keel_disconnect.py`",
                    "why": ("`make down` and every other door end by asking the skill's own way "
                            "out and proving `agent.connected` went false within two seconds "
                            "(spec 011). Here nothing was ever connected: shelling that script "
                            "would be asserting something about a repository this door does not "
                            "touch, against a home it never wrote in."),
                    "what stands in its place": ("the empty KEEL_HOME above, which is the same "
                                                 "claim made from the other end")})
        else:
            # ------------ spec 024 FR-002, read the other way round: keel-cloud's own `execution`
            # report must name **this cell's host**, never `api`. It is the same document the Keel
            # door is judged by, and on these doors it is the cloud's own independent
            # corroboration that the runner's CLI did the thinking. A cell that had quietly become
            # a KEEL account -- the fault spec 024 found -- would report `api` here and nowhere
            # else, while every runtime artefact went on saying exactly what it always said.
            with recorder.step(f"spec 024: keel-cloud reports every job as {HOST}'s own, never as "
                                "Keel's AI", party="stack", kind="assert") as h:
                # Same correction as the Keel door's, and here it had been worse than wrong: the
                # filter tested `job["execution"]` on the interaction list's stub, which never has
                # that key, so `cloud_side` was always empty and this step asserted **nothing**
                # while reading green. It fetches each job's own detail now, and the jobs that
                # carry no report at all (keel-runtime before 0.5.0) are counted and named.
                fetched = keels_ai.jobs_with_their_execution(_get, interactions)
                cloud_side = [r for r in fetched if r["host"]]
                not_this_host = [r for r in cloud_side if r["host"] != HOST]
                h.record_assert({"execution.host": HOST, "jobs answered elsewhere": []},
                                 {"jobs read": len(fetched),
                                  "jobs carrying an execution report": len(cloud_side),
                                  "per job": fetched,
                                  "jobs answered elsewhere": not_this_host,
                                  "why none of them is not a pass and not a failure": (
                                      f"keel-runtime reports `execution` from 0.5.0 (spec 042); "
                                      f"this run's bundled runtime is {runtime_stamp}, and an "
                                      f"older one reports nothing at all. The startup line and "
                                      f"the per-job envelopes above are what stand in for it")})
                assert not not_this_host, (
                    f"keel-cloud says a job of this journey was answered by "
                    f"{sorted({r['host'] for r in not_this_host})} and not by {HOST!r}. `api` "
                    f"there means this account runs on Keel's own AI (keel-cloud spec 045 "
                    f"FR-043) -- i.e. the cell came in through the wrong door and keel-cloud is "
                    f"spending Keel's Anthropic key on a founder who has their own CLI.")

            with recorder.step("what it cost, in this host's own unit and never converted into the "
                                "other's (C-7)", party="stack", kind="note") as h:
                rows = canary_mod.wait_for_envelopes(keel_home, timeout_s=180)
                per_job = []
                for row in rows:
                    facts = host.envelope_facts(row["envelope"])
                    per_job.append({"job_id": row["job_id"], **facts})
                caps = canary_mod.cap_sources(stack.keel_runtime, keel_home)
                spend = {"host legs": [run.spend() for run in (first, second)],
                         "people": len(people_chosen),
                         "readings scale with people": (
                             "one reading job an answered anchor, on the routing table's light model "
                             "where the cloud has a row for this host (model-routing-design.md §3)"),
                         "thinking (keel-runtime jobs)": [
                             {k: v for k, v in row.items()
                              if k in ("job_id", "premium_requests", "total_cost_usd", "model")}
                             for row in per_job],
                         "jobs": len(rows),
                         "pinned_model (runtime)": model,
                         "pinned_model (host)": host_model,
                         "reported model (host)": second.model,
                         "cap sources": caps}
                h.record_wire({"per job": per_job}, spend)
                (run_dir / "spend.json").write_text(json.dumps(
                    {"host": HOST, **spend, "per job": per_job}, indent=2) + "\n")
                errored = [r for r in per_job if r["is_error"]]
                assert per_job, "the runtime wrote no job envelopes at all"
                assert not errored, f"a keel-runtime job envelope reports an error: {errored}"

            # ------------------------------------------- the model each job asked for is the cloud's
            # keel-cloud model-routing-design.md §10 step 3: on a runtime that reads the job's `model`
            # key, what every job *requested* must be exactly what the cloud's table names for this
            # host and that job's class -- and `None`, the CLI's default, where the table has no
            # entry (it ships empty). The job's class comes from the interaction the cloud reports
            # for it, its screen mapped the way `InferenceScreen.jobClass()` maps it. Not a loosened
            # assertion: an older runtime, or a checkout with no table yet, is a note that says which,
            # never a pass.
            screen_by_job = {(i.get("job") or {}).get("job_id"): i.get("screen")
                             for i in interactions if i.get("job")}
            requested = []
            for row in rows:
                facts = models_mod.job_model_facts(keel_home / "jobs" / row["job_id"])
                screen = screen_by_job.get(row["job_id"])
                expected = (routing_table.resolve_screen(HOST, screen)
                            if routing_table is not None and screen else None)
                requested.append({"job_id": row["job_id"], "screen": screen,
                                  "class": models_mod.SCREEN_TO_CLASS.get(screen or ""),
                                  "expected": expected, **facts})
            if routing_runtime and routing_table is not None:
                with recorder.step("every job requested the model keel-cloud's own table names for "
                                    "this host and its class (model-routing-design §10 step 3)",
                                    party="stack", kind="assert") as h:
                    known = [r for r in requested if r["screen"]]
                    wrong = [r for r in known if r["model_requested"] != r["expected"]]
                    h.record_assert({"jobs off the table": []},
                                    {"per job": requested, "jobs off the table": wrong,
                                     "table": routing_table.source})
                    assert known, "no job could be tied to a screen, so nothing was checked"
                    assert not wrong, (
                        f"a job asked for a model the cloud's table does not name for {HOST}: {wrong}")
            else:
                with recorder.step("the model routing check does not apply here, and this is why",
                                    party="stack", kind="note") as note:
                    note.record_wire(None, {
                        "per job": requested,
                        "why": (f"keel-runtime {runtime_stamp} is older than 0.5.0 and reads no "
                                "job `model` key" if not routing_runtime else
                                "keel-cloud has no model-routing.json on this checkout")})
                # **The second, independent proof that this host did the thinking** -- where the
                # envelope can carry it. `CopilotExecutor._envelope` stamps `executor` on every job,
                # written by the process that ran it, so the startup line says which executor was
                # *chosen* and this says which one *answered*. `ClaudeCodeExecutor` passes the CLI's
                # own `result` event through unchanged and that event names no executor, so on that
                # host the cross-check does not exist and the bundle says so rather than the scenario
                # quietly asserting less on both.
                if host.envelope_names_its_executor:
                    wrong_host = [r for r in per_job if r["executor"] != EXPECTED_EXECUTOR]
                    assert not wrong_host, (
                        f"a job was answered by an executor that is not {EXPECTED_EXECUTOR!r}: "
                        f"{wrong_host}")
                else:
                    with recorder.step("...and on this host the per-job envelope names no executor "
                                        "at all, so the startup line is the only reading there is",
                                        party="stack", kind="note") as note:
                        note.record_wire(None, {"envelope keys": sorted(rows[0]["envelope"] or {}),
                                                "why": per_job[0]["why"]})
            print(f"\nS-012 {LEGS} journey through {HOST} as {founder.project_name!r} "
                  f"({entry.id}): {len(rows)} jobs; "
                  f"host legs {[run.spend() for run in (first, second)]}; "
                  f"runtime model {model or 'unpinned (this executor takes none)'}")

            # ------------------------------------------------------------------- the way a founder goes
            with recorder.step('§1.0: "keel disconnect" against this run\'s own home',
                                party="stack", kind="assert") as h:
                outcome = stack_runtime.disconnect_via_skill_script(stack, home=keel_home, timeout=60)
                after = _status()
                h.record_assert({"outcome": "disconnected", "running after": False},
                                 {"disconnect": outcome, "after": after})
                assert outcome is not None, (
                    "keel-connect-skill's own way out answered nothing at all")
                assert outcome.get("outcome") in stack_runtime.STOPPED_OUTCOMES, (
                    f"the runtime did not stop: {outcome}")
                assert not after.get("running", False), (
                    f"disconnect answered {outcome.get('outcome')!r} but status still reads running: "
                    f"{after}")

        passed = True
    finally:
        context.close()
        shutil.rmtree(host.work_dir, ignore_errors=True)
        # Spec 017 / e2e-matrix-design §6.4: the verdict goes onto the cell's own founder in the
        # twin's chooser, so the founder's morning picker reads it. Local profiles: no I/O.
        if stack.is_remote:
            verdict = "PASSED" if passed else f"FAILED at {recorder.failed_step or 'an unnamed step'}"
            try:
                remote.label_cell_identity(stack, founder_one.id, f"{cell_label} — {verdict}")
            except Exception as exc:  # noqa: BLE001 - the label is evidence, never the verdict
                print(f"\ncould not label the cell's founder in the chooser: {exc}")
        # `facts.json` is the scorer's own registry and this scenario is unscored, so it would
        # otherwise be `{}`. One string goes in beside it -- a *string*, so `scoring.read_facts`
        # skips it rather than reading an empty Fact out of it -- because a bundle whose verdict
        # says `s012-journey-claude` should say which host, which CLI and which model in the
        # file a reader opens next. The structured record is `versions.json`'s `host` block.
        finalize_run(run_dir, slug=BUNDLE, passed=passed,
                     facts={"the journey's host": (
                         _the_keel_door_in_one_line() if KEELS_AI else
                         f"{HOST} · {ready['version']} · host model "
                         f"{host_model or 'the account default, recorded not pinned'} · runtime "
                         f"model {model or 'unpinned (this executor takes none)'}"),
                            "the journey's founder": (
                         f"{ENTRY_ID} · {founder.project_name} · "
                         f"{founder.market.country} · "
                         + (f"{len(people_chosen)} people, {', '.join(people_names)}"
                            if not SHORT else "nobody invited (short)")),
                            "the journey's length": (
                         f"{LEGS} · " + (agent_host.short_stops_at(HOST) if SHORT else
                                          "both legs, whole")),
                            **({"what the framing measured": _what_the_framing_measured()}
                               if KEELS_AI and SHORT else {})},
                     failed_step=recorder.failed_step, duration_s=_now() - started)
        print(f"\nrun bundle: {run_dir}")
