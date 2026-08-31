"""S-010 -- the shaping mandates are actually on the wire (Layer 1 of specs/shaping-eval-design.md).

Downstream of keel-cloud's hypothesis-shaping-design.md (v2, instruction-only): the whole feature
is CREATE/FRAME/INTRODUCE_ASSUMPTIONS `instruction.content` in `src/main/resources/keel/
v2-instructions.yaml`, so the only thing a deterministic, no-LLM harness can honestly prove is
**delivery** -- these mandates are actually served in the wire's `instruction.content` -- never
**efficacy** (does a real agent actually refuse vagueness?). That harder question is Layer 2's
job (`evals/test_shaping_gauntlet.py`, `make eval-shaping`, opt-in, never here). Design §1's own
words: "Cheap, honest about what it proves: delivery, not efficacy."

This scenario walks a fresh project through CREATE, one later-stage FRAME (SOLUTION -- FRAME's
instruction content is one shared blob covering problem/solution/commercial alike, per the yaml,
so a later stage's issuance proves the same mandate keeps arriving stage after stage, not just on
the very first framing), and INTRODUCE_ASSUMPTIONS, and asserts each issuance's own
`instruction.content` carries 2-3 stable, meaning-bearing marker phrases lifted verbatim from the
current yaml text -- not paraphrased, so a future edit that actually drops the mandate fails this
test, while a future rewording that keeps the mandate's substance is expected to need a marker
update too (the markers are pinned to today's wording on purpose).

No journey moment is cited here on purpose (module docstring, not a journey-coverage comment):
hypothesis-shaping-design.md's own §7 table says the eval note is "structural checks only ...
ledger untouched (no new journey moment -- §1.1 deepens)". This scenario is exactly that
structural check; CANON.md's ledger gets no new row, and journeys.md §1.1 ("it keeps asking...")
is what this test's CREATE/FRAME markers are proof of the *depth* of, not a new moment in its own
right.

Protocol-only, no browser (S-007's shape): the claim under test lives entirely in
`instruction.content`, which no screen ever renders, so there is nothing for a browser to add.
Scored like S-007 -- only agent-surface categories (ORIENTATION/GUIDANCE via ORI-A1/GUI-A1 on
each agent-cycle interaction) ever have evidence; FIDELITY/CLARITY-U/participant checks are
`not_applicable_categories`, named rather than silently zeroed (`evals/policy.py`'s existing
design, `harness/scoring.not_applicable_categories`).
"""

from __future__ import annotations

import time

from evals.scenario import Scenario
from harness.driver import FounderAgentDriver
from harness.evidence import finalize_run
from harness.steps import Recorder

ROLE_LABEL = "Independent Restaurant Manager"

# Marker phrases (module docstring): 2-3 per entry, lifted verbatim (case-insensitive, whitespace-
# normalized) from keel-cloud's src/main/resources/keel/v2-instructions.yaml as it reads today.
# FRAME's content is one shared blob for every stage (problem/solution/commercial guidance all in
# one paragraph) -- these three markers span all three clauses on purpose, so a SOLUTION-stage
# FRAME issuance (this scenario's "later stage") still proves the whole mandate arrived, not just
# the solution clause.
CREATE_MARKERS = [
    "quantifiable: who has it, when it shows up, how often, and what it costs",
    "a named unknown is a legitimate discovery target",
    "a faked number poisons every verdict downstream",
]
FRAME_MARKERS = [
    "a problem claim must be quantifiable",
    "a solution claim must not be a product label",
    "if the mechanism cannot be said in a sentence, the claim is not ready to test",
]
ASSUMPTIONS_MARKERS = [
    "cluster semantically overlapping candidates and merge those testing substantially the same uncertainty",
    "split any compound that can fail in independent ways",
    "bad, inefficient, important, useful, easy and their cousins are banned unless the statement defines them operationally",
]


def _normalize(text: str) -> str:
    return " ".join((text or "").split()).lower()


def _assert_markers(recorder: Recorder, label: str, content: str, markers: list[str]) -> None:
    with recorder.step(f"{label} instruction.content carries the shaping mandate", party="agent",
                        kind="assert") as h:
        normalized = _normalize(content)
        missing = [m for m in markers if m not in normalized]
        h.record_assert({"markers": markers}, {"content": content})
        if missing:
            h.fail(f"{label} instruction.content is missing marker phrase(s) {missing!r} -- "
                   f"got: {content!r}")
            raise AssertionError(h.error)


class S010ShapingDelivery(Scenario):
    """Only the hooks this walk actually calls (CREATE, FRAME, INTRODUCE_ROLES) are implemented --
    the scenario never submits INTRODUCE_ASSUMPTIONS itself (it only reads that issuance's own
    instruction.content), so assumptions_payload/interpret_payload/brief_payload/about_line/etc.
    are never called and stay the base class's NotImplementedError, matching this scenario's own
    "cheap" design goal (module docstring): a fresh, never-completed project is enough to prove
    delivery."""

    name = "S-010 shaping delivery"
    slug = "s010-shaping-delivery"

    def project_name(self) -> str:
        return "Shelf Reconciliation Radar"

    def problem_statement(self) -> str:
        return ("Independent restaurant managers lose one to two hours a month reconciling "
                "physical against recorded inventory.")

    def frame_statement(self, stage: str) -> str:
        return {
            "SOLUTION": "A tool that scans shelf counts and compares them against the POS "
                        "system's own numbers, flagging the mismatches for a manager to resolve.",
            "COMMERCIAL": "Independent restaurant managers would pay a monthly fee once it "
                          "reliably catches mismatches before month-end close.",
        }[stage]

    def roles_payload(self) -> list[dict]:
        return [{
            "label": ROLE_LABEL,
            "roleType": "MANAGER",
            "about": "How they reconcile physical shelf counts against what the POS system records",
        }]

    def facts(self) -> dict:
        return {}  # Layer 1 is about instruction delivery only -- no fact registry to trace.


def test_s010_shaping_delivery(stack, run_dir, founder_credentials):
    recorder = Recorder(run_dir)
    scenario = S010ShapingDelivery()
    cloud_base = f"http://localhost:{stack.cloud_port}"

    driver = FounderAgentDriver(cloud_base, recorder, scenario, agent_key=founder_credentials.agent_key)
    passed = False
    started = time.monotonic()
    try:
        # CREATE frames PROBLEM as a side effect (harness/driver.py's own derivation of the real
        # choreography): its own instruction.content is where the problem-quantifiability mandate
        # lives.
        create_resp = driver.advance_one()
        assert create_resp.get("kind") == "action" and create_resp.get("action") == "CREATE", create_resp
        _assert_markers(recorder, "CREATE", (create_resp.get("instruction") or {}).get("content", ""),
                         CREATE_MARKERS)

        # The opening pass's next FRAME is SOLUTION, never PROBLEM again (CREATE already framed
        # it) -- a later stage than CREATE's own PROBLEM framing, and proof the same mandate
        # keeps arriving stage by stage, not only once.
        frame_resp = driver.advance_one()
        assert frame_resp.get("kind") == "action" and frame_resp.get("action") == "FRAME", frame_resp
        assert (frame_resp.get("detail") or {}).get("stage") == "SOLUTION", frame_resp
        _assert_markers(recorder, "FRAME (SOLUTION)", (frame_resp.get("instruction") or {}).get("content", ""),
                         FRAME_MARKERS)

        # FRAME COMMERCIAL and INTRODUCE_ROLES follow the same real sequence (harness/driver.py's
        # module docstring): advance through both so the next recommendation is legitimately
        # INTRODUCE_ASSUMPTIONS for PROBLEM.
        driver.advance_one()  # FRAME COMMERCIAL
        driver.advance_one()  # INTRODUCE_ROLES (roles ladder, project-wide, once)

        # Read INTRODUCE_ASSUMPTIONS's own issuance without submitting it -- this scenario only
        # needs to prove the normalization-pass mandate arrived, never a completed discovery.
        with recorder.interaction("agent-cycle"):
            issuance = driver.get_next()
        assert issuance.get("kind") == "action" and issuance.get("action") == "INTRODUCE_ASSUMPTIONS", issuance
        assert (issuance.get("detail") or {}).get("stage") == "PROBLEM", issuance
        _assert_markers(recorder, "INTRODUCE_ASSUMPTIONS",
                         (issuance.get("instruction") or {}).get("content", ""), ASSUMPTIONS_MARKERS)

        passed = True
    finally:
        duration = time.monotonic() - started
        finalize_run(run_dir, scenario=scenario, passed=passed,
                     failed_step=recorder.failed_step, duration_s=duration)
        print(f"\nrun bundle: {run_dir}")
