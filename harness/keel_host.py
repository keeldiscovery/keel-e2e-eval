"""The host that is not a host (spec `024-keels-ai-cell`; keel-cloud
`canon/designs/ai-credits-design.md` §6, spec `044-ai-credits`, spec `045-keels-ai-executor`).

**"The door decides the AI."** A founder who says *keel connect* to Claude Code, Copilot or Codex
is on their own AI: they install a plugin, load a skill, approve a device, and a runtime on their
own machine answers every job with their own model on their own plan. A founder who signs up with
Google at keel-web's `/signup` is on **Keel's** AI: keel-cloud marks the account `ai_path = KEEL`
from the door alone (spec 044 FR-014), grants 1,500 credits once (FR-017), and answers every job
in process on Keel's own Anthropic account (spec 045).

The journey between those two founders is the same journey -- describe the idea, approve the
lines, invite people, answer as them, read, brief -- so S-012 is widened by a **door**, exactly as
spec 019 widened it by a host and spec 022 by a packaging. This module is that door's side of
`harness/agent_host.py`'s interface, and almost all of it is a refusal.

**Three rules, and they are the other three hosts' three rules read backwards.**

1. **No implementation here ever starts the runtime** -- and here there is no runtime to start,
   ever, by anybody. `KEEL_HOME` is created empty and the scenario asserts it is still empty when
   the brief is written. That emptiness is the strongest evidence in the bundle: on this door,
   *nothing started* is not an absence of proof, it is the proof.

2. **Nothing here reads prose for evidence.** There is no host reply to read. What answered is
   read off keel-cloud's own `execution` report on each job -- `host: "api"`, the model ids, and
   `actual_cost_micro_usd` -- which the executor writes and neither the founder, nor the model,
   nor this harness can.

3. **The credential is never copied, and here there is none to copy.** The key is
   `KEEL_ANTHROPIC_API_KEY` on the twin, it belongs to keel-cloud, and it never leaves that box.
   The founder has no credential on this road at all -- that is what the road is *for* -- and
   `credential_plan` says exactly that rather than leaving a reader to guess.

**Every host-leg method raises.** `add_marketplace`, `install_plugin`, `plugin_list`,
`skill_proof`, `install_extension`, `extension_proof` and `say` are not silently no-ops returning
an empty dict, because a no-op is how a skipped assertion becomes a passed one. They raise
`NoHostHere` with a sentence naming this spec, so a future edit that reaches for leg one on this
door finds out at the first call instead of in a green bundle.
"""

from __future__ import annotations

from typing import Any

from harness.agent_host import AgentHost, HostRun


class NoHostHere(RuntimeError):
    """Something asked the Keel door for a host-leg thing: a marketplace, a plugin, a skill
    listing, a Spec Kit extension, or three words said to a CLI.

    Deliberately an error and never an empty answer. Leg one is **skipped** on this door, and the
    difference between *skipped* and *asserted loosely* is the whole of this scenario's evidence
    discipline. A method here that returned `{"found": False}` would let a future edit assert
    something about an install that never happened and pass.
    """


class KeelHost(AgentHost):
    """Keel's own AI, behind the Google door. It installs nothing, says nothing, and runs nothing.

    It exists so the scenario can keep one shape across four doors: it is asked the same three
    questions every host is asked before the journey starts -- *are you ready*, *which executor
    must the wire report*, *how is this run authenticated* -- and it answers all three truthfully
    without a subprocess.
    """

    name = "keel"
    #: There is no binary. Named as the empty string rather than `None` because
    #: `AgentHost.__init__` runs it through `shutil.which`, and `which("")` is `None`, which is
    #: what the bundle should say.
    binary = ""
    #: There is no host home and therefore no variable that moves one.
    home_var = ""
    #: What keel-cloud's own executor reports as `execution.host` (spec 045 FR-043). Not `keel`:
    #: that is the door's name, which is the cell's and the bundle's. See
    #: `agent_host.EXECUTOR_FOR_HOST`.
    executor = "api"
    #: There are no per-job envelopes at all here -- no runtime wrote any. What names the executor
    #: is keel-cloud's `execution` block on the job, read off the wire, which is a different
    #: document and is not pretended to be this one.
    envelope_names_its_executor = False
    forbidden_flags = ()
    stdin_devnull = False
    #: keel-cloud's own `keel.v2.keels-ai.job-timeout` is moving from `PT300S` to `PT600S`
    #: (measured on the staging twin, run 36625025566, 2026-09-29): the assumptions job behind the
    #: COMMERCIAL review card was measured there at ~280-290s at effort xhigh, close enough to the
    #: old 300s ceiling that keel-cloud is raising it. 660 covers the new 600s ceiling plus the
    #: same order of margin the old 480s (300 + 180) kept over the old one; the BRIEF job's own
    #: wait -- S-012's other in-process job on this door -- is raised the same way and for the same
    #: reason (spec 024 FR-010). The three CLI hosts are untouched: `AgentHost.keels_ai_job_wait_s`
    #: stays 480 for them, because none of their jobs run against keel-cloud's clock at all.
    keels_ai_job_wait_s = 660.0

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        #: Counted so the scenario can assert it, rather than asserted by reading this file.
        #: Nothing increments it; every method that could is a refusal.
        self.subprocesses_run = 0

    # ------------------------------------------------------------------------------- readiness

    @staticmethod
    def readiness(**kwargs) -> dict[str, Any]:  # noqa: ARG004 - the interface's keywords
        """**Always ready, and it costs nothing to say so.**

        Every other host's `readiness` exists to answer *is the CLI there and can a fresh home
        authenticate*, because the alternative is a paid run discovering it. Neither question has
        a subject here: there is no CLI to be absent and no home to authenticate. Whether the
        **door** is open is keel-cloud's to answer and it answers it on the first job, by name
        (spec 045 FR-032's `KEEL_AI_DISABLED`), which the scenario reads and fails fast on -- a
        thing this method could not find out without spending anyway.
        """
        return {
            "ok": True,
            "reason": None,
            "version": None,
            "binary": None,
            "why": ("there is no host CLI on this door: the founder signed up with Google and "
                    "keel-cloud answers every job on its own account (spec 045). Whether that "
                    "account's key is present is keel-cloud's to say, and it says it by name on "
                    "the first job."),
        }

    @staticmethod
    def model_accepted(slug: str) -> bool:  # noqa: ARG004
        """Nothing here pins a model and nothing here probes one. keel-cloud chooses the model per
        screen class from its own routing table (spec 045 FR-016/FR-018) and reports what answered
        in `execution.model_used`, which the bundle records and asserts nothing about."""
        return True

    # ------------------------------------------------------------------- the environment, and none

    def _runtime_model_env(self) -> dict[str, str]:
        """No pin travels anywhere: there is no executor process to carry one to."""
        return {}

    def write_home_config(self) -> None:
        """**Writes nothing, on purpose.**

        The other three hosts write `<KEEL_HOME>/config.json` so the runtime the skill starts and
        the runtime this harness later asks are provably the same Keel. There is no runtime here,
        and a `config.json` in this run's `KEEL_HOME` would be the one thing in it -- which would
        cost the scenario its cleanest assertion, that the home the door was given is **empty**
        from the first screen to the last.
        """
        return None

    # ------------------------------------------------------ leg one, which does not happen here

    def _no_host(self, what: str) -> NoHostHere:
        return NoHostHere(
            f"{what} was asked of the Keel door, which has no host CLI, no plugin, no skill and "
            f"no runtime (spec 024-keels-ai-cell; keel-cloud ai-credits-design.md §6). Leg one is "
            f"skipped on this door -- not asserted loosely, and not answered with an empty "
            f"result that would read as a pass.")

    def add_marketplace(self, source: str | None = None) -> dict:  # noqa: ARG002
        raise self._no_host("`plugin marketplace add`")

    def install_plugin(self, spec: str | None = None) -> dict:  # noqa: ARG002
        raise self._no_host("`plugin install`")

    def plugin_list(self) -> dict:
        raise self._no_host("`plugin list`")

    def skill_proof(self) -> dict:
        raise self._no_host("the skill proof")

    def install_extension(self, source_tree) -> dict:  # noqa: ARG002
        raise self._no_host("the Spec Kit extension install")

    def extension_proof(self) -> dict:
        raise self._no_host("the Spec Kit extension proof")

    def say(self, prompt: str, *, slug: str, timeout: float = 420) -> HostRun:  # noqa: ARG002
        raise self._no_host('"keel connect"')

    def _say_argv(self, prompt: str, *, usage_path) -> list[str]:  # noqa: ARG002
        raise self._no_host("an argv")

    # ---------------------------------------------------------------------- what the bundle says

    def credential_plan(self) -> dict:
        """**None, and that is the road's whole point.**

        `ai-credits-design.md` §6.1's own column: *"Nothing to install"*. There is no login for
        this harness to measure, no isolated home to wonder about, and no secret in this process.
        The one key involved is `KEEL_ANTHROPIC_API_KEY` on the twin; it is keel-cloud's, it is
        read through the SDK's explicit builder and never from the process environment (spec 045
        FR-032), and it never appears in a log, an error, an `execution` block or a bundle.
        """
        return {
            "how": ("none -- the founder has no credential on this road and neither has this "
                    "harness. keel-cloud answers every job on its own Anthropic account, with a "
                    "key that lives on the twin and never leaves it (spec 045 FR-029, FR-033)."),
            "variable": None,
            "isolated_home": False,
        }

    def envelope_facts(self, envelope: dict | None) -> dict:
        """There are no per-job envelopes on this door: no runtime ran, so nothing wrote one.

        The equivalent reading is keel-cloud's own `execution` block on each job, which the
        scenario takes off the wire (`harness/keel_host.py::execution_facts`). This method keeps
        the interface honest by saying so rather than returning a shape that looks like a reading.
        """
        raise self._no_host("a keel-runtime job envelope")


#: The four reasons spec 045 gives for a job that could not run, and the exact words they travel
#: in. None of them is an `error.code` -- spec 045 Assumption 11 is explicit that the five wire
#: codes are not extended, because a sixth would be a founder-visible vocabulary change keel-web
#: has no spec for. They ride in `error_message` (and in the `REFUND` row's `reason`), which is
#: free text, so the reading is of the message and the code beside it is one of the five.
#:
#: Named here rather than in the scenario so `make unit` can hold the list, and so the day a fifth
#: reason is added there is one place to add it.
NAMED_REASONS = {
    "KEEL_AI_DISABLED": (
        "keel-cloud has no KEEL_ANTHROPIC_API_KEY, so Keel's AI is switched off on this "
        "deployment and the job failed before a socket was opened (spec 045 FR-032)"),
    "KEEL_AI_DAILY_CAP": (
        "this founder has reached keel.v2.keels-ai.daily-cap-micro-usd for the UTC day "
        "($10.00 by default), so the job failed before a call was made (spec 045 FR-037)"),
    "KEEL_AI_TIMEOUT": (
        "the job's wall clock reached keel.v2.keels-ai.job-timeout (PT300S by default) and it "
        "was abandoned and refunded (spec 045 FR-039)"),
    "KEEL_AI_RESTARTED": (
        "keel-cloud restarted while this job was RUNNING; the startup sweep failed it and "
        "refunded it (spec 045 FR-009)"),
}


def execution_facts(job: dict | None) -> dict:
    """What **keel-cloud's own `execution` report** says about who answered a job and what it cost.

    The counterpart of the other three hosts' `envelope_facts`, and deliberately not called that:
    it reads a different document, written by a different process, off the wire rather than off a
    runtime home. `job` is the `job` object a `/v2/inference-interactions` row carries.

    `host` must read `api` (spec 045 FR-043), `actual_cost_micro_usd` must be present and above
    zero (FR-023/FR-025; FR-027 makes zero mean *failed before any call*, which is a finding and
    not a pass), and the two model ids are recorded and asserted against nothing -- keel-cloud
    chooses them from its own routing table and this repository cannot see that table.
    """
    job = job or {}
    execution = job.get("execution") or {}
    cost = execution.get("actual_cost_micro_usd")
    # **Whatever timing the wire happens to carry, and no invention.** keel-cloud's `execution`
    # object is five strings, a boolean and the cost (spec 045 FR-043; design §15 amendment 1) --
    # it carries **no token counts**, so a bundle that printed any would be printing a number
    # nobody reported. The job row's own timestamps are a different matter: they are whatever
    # keel-cloud puts there, so they are picked up if present and named absent if not, and the
    # scenario records its own wall clock beside them either way.
    timing = {key: job.get(key) for key in
              ("created_at", "started_at", "completed_at", "updated_at", "duration_ms")
              if job.get(key) is not None}
    return {
        "job_id": job.get("job_id"),
        "status": job.get("status"),
        "timing, as keel-cloud reported it": timing or None,
        "tokens": None,  # not on the wire at all -- see the comment above.
        "host": execution.get("host"),
        "host_version": execution.get("host_version"),
        "model_requested": execution.get("model_requested"),
        "model_used": execution.get("model_used"),
        "retried_unpinned": execution.get("retried_unpinned"),
        "actual_cost_micro_usd": cost,
        "cost_reported": isinstance(cost, int) and not isinstance(cost, bool),
        "error": job.get("error"),
    }


def named_reason(text: str | None) -> str | None:
    """Which of spec 045's four named reasons a failure's `error_message` carries, or `None`.

    A substring read, because the message is the composite `"<CODE>: <REASON>"` -- e.g.
    `"LLM_UNAVAILABLE: KEEL_AI_DISABLED"` -- and keel-cloud is free to say more around it.
    """
    haystack = text or ""
    for reason in NAMED_REASONS:
        if reason in haystack:
            return reason
    return None
