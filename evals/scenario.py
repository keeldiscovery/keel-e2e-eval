"""Scenario base (T012, data-model.md): payload builders keyed by action, an answer table for the
participant, and an about-line. A concrete scenario is "a matter of one new module" (FR-007) --
subclass this, fill in the hooks, write a `evals/test_*.py` that drives it.
"""

from __future__ import annotations

from typing import Any


def find_role(roles: list[dict], label: str) -> dict:
    for role in roles:
        if role["label"] == label:
            return role
    raise KeyError(f"no role named {label!r} among {[r['label'] for r in roles]}")


class Scenario:
    """Consulted by harness.driver.FounderAgentDriver -- never generates content itself, only
    picks from what it was built with (FR-003: "no LLM anywhere").
    """

    name: str = "unnamed scenario"
    slug: str = "unnamed"

    def build_payload(self, action: str, detail: dict, context: dict[str, Any]) -> dict:
        stage = detail.get("stage")
        if action == "CREATE":
            return {"statement": self.problem_statement()}
        if action == "FRAME":
            return {"stage": stage, "statement": self.frame_statement(stage)}
        if action == "INTRODUCE_ROLES":
            return {"roles": self.roles_payload()}
        if action == "INTRODUCE_ASSUMPTIONS":
            roles = context["roles"]["roles"]
            return {"assumptions": self.assumptions_payload(stage, roles)}
        if action == "INTERPRET":
            response = context["response"]
            return {
                "invitationId": detail["invitationId"],
                "perAnswer": self.interpret_payload(stage, response),
            }
        if action == "PROCEED_TO_BRIEF":
            return self.brief_payload(context)
        raise NotImplementedError(f"{type(self).__name__} has no payload builder for {action!r}")

    # ---------------------------------------------------------------------------- hooks to fill in

    def problem_statement(self) -> str:
        raise NotImplementedError

    def frame_statement(self, stage: str) -> str:
        raise NotImplementedError

    def roles_payload(self) -> list[dict]:
        raise NotImplementedError

    def assumptions_payload(self, stage: str, roles: list[dict]) -> list[dict]:
        raise NotImplementedError

    def interpret_payload(self, stage: str, response: dict) -> list[dict]:
        raise NotImplementedError

    def brief_payload(self, context: dict[str, Any]) -> dict:
        raise NotImplementedError

    def fix_schema(self, action: str, payload: dict, problem: str) -> dict:
        """Optional hook: a scenario that expects a particular schema refusal can correct and
        return a fixed payload. The default has none to offer -- a schema violation out of a
        deterministic builder is a driver bug, not a runtime condition."""
        raise NotImplementedError(f"no schema fix available for {action}: {problem}")

    # ------------------------------------------------------------------- participant-facing data

    def about_line(self, stage: str) -> str:
        raise NotImplementedError

    def person_name(self, stage: str) -> str:
        raise NotImplementedError

    def participant_answer(self, stage: str) -> str:
        """The single supportive free-text answer this scenario's participant gives to every
        question on a stage's invitation (S-001 answers supportively throughout)."""
        raise NotImplementedError
