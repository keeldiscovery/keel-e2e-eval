"""Derives scored Interaction objects from a tagged transcript (data-model.md's "Interaction
(derived, harness/interactions.py)"). Pure function of `transcript.jsonl` entries -- no wire
calls, no clock -- so `make report RUN=<dir>` can re-derive interactions (and therefore re-score)
from an old bundle alone (FR-007, SC-004).

A transcript with no `interaction` tags at all -- a pre-002 bundle, or one built by a step that
never opened an interaction scope -- derives to an empty list rather than raising (analysis
finding A2): `harness/rubric.py` and `harness/scoring.py` both treat "no interactions" as a valid,
if uninformative, scorecard (every category empty, run_score 0.0), not a crash.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class Interaction:
    id: str
    type: str  # agent-cycle | agent-handoff | ui-visit | participant-page | fidelity-summary
    title: str
    party: str
    step_seqs: list[int] = field(default_factory=list)
    screenshots: list[str] = field(default_factory=list)
    conversation: dict[str, Any] | None = None
    captured_text: dict[str, str] = field(default_factory=dict)
    # Not part of data-model.md's serialized shape (scorecard.json only carries id/type/title/
    # attributes/checks) -- kept here so harness/rubric.py can inspect the raw protocol
    # request/response bodies a check needs (e.g. ORI-A1's instruction.content) without
    # re-parsing the transcript itself.
    entries: list[dict] = field(default_factory=list, repr=False)


def _merge_captured_text(entries: list[dict]) -> dict[str, str]:
    merged: dict[str, str] = {}
    for entry in entries:
        for source, text in (entry.get("captured_text") or {}).items():
            if not text:
                continue
            if source not in merged:
                merged[source] = text
            elif text not in merged[source]:
                merged[source] = f"{merged[source]}\n{text}"
    return merged


def _last_matching(entries: list[dict], *, kind: str, name_prefix: str) -> dict | None:
    for entry in reversed(entries):
        if entry.get("kind") == kind and str(entry.get("name", "")).startswith(name_prefix):
            return entry
    return None


def _first_matching(entries: list[dict], *, kind: str, name_prefix: str) -> dict | None:
    for entry in entries:
        if entry.get("kind") == kind and str(entry.get("name", "")).startswith(name_prefix):
            return entry
    return None


def _summarize_payload(payload: Any, *, _depth: int = 0) -> str:
    """A founder-readable rendering of a submitted payload -- every string leaf, in order, joined
    into a sentence-ish blob (scorecard-contract.md: "the scripted founder reply (summarized from
    the submitted payload)"). Deliberately not a JSON dump: the conversation card exists so a
    reviewer sees prose, not braces; raw JSON stays available, collapsed, alongside it.
    """
    if _depth > 6 or payload is None:
        return ""
    if isinstance(payload, str):
        return payload
    if isinstance(payload, (int, float, bool)):
        return str(payload)
    if isinstance(payload, dict):
        parts = [_summarize_payload(v, _depth=_depth + 1) for v in payload.values()]
        return "; ".join(p for p in parts if p)
    if isinstance(payload, list):
        parts = [_summarize_payload(v, _depth=_depth + 1) for v in payload]
        return "; ".join(p for p in parts if p)
    return str(payload)


def _response_body(entry: dict | None) -> dict:
    if entry is None:
        return {}
    response = entry.get("response")
    if isinstance(response, dict):
        body = response.get("body")
        if isinstance(body, dict):
            return body
    return {}


def _agent_cycle_conversation(entries: list[dict]) -> dict[str, Any]:
    issuance = _first_matching(entries, kind="protocol", name_prefix="get_next")
    body = _response_body(issuance)
    instruction = body.get("instruction") or {}
    submit_entry = _last_matching(entries, kind="protocol", name_prefix="submit ")
    outcome = None
    reply_summary = None
    if submit_entry is not None:
        submit_request = submit_entry.get("request") or {}
        reply_summary = _summarize_payload((submit_request or {}).get("body", {}).get("payload"))
        submit_response_body = _response_body(submit_entry)
        if submit_response_body.get("revision") is not None:
            outcome = f"committed revision {submit_response_body['revision']}"
        elif submit_entry.get("error"):
            outcome = f"refused: {submit_entry['error']}"
    return {
        "instruction": {"purpose": instruction.get("purpose"), "content": instruction.get("content")},
        "requirements": body.get("requirements") or [],
        "reply_summary": reply_summary,
        "outcome": outcome,
        # Extra, beyond data-model.md's minimum shape: harness/rubric.py's ORI-A2 (stage/
        # invitation-scoped detail) and CLA-A1 need the raw action/detail without re-parsing
        # entries themselves.
        "action": body.get("action"),
        "detail": body.get("detail") or {},
    }


def _shaping_turn_conversation(entries: list[dict]) -> dict[str, Any]:
    """The shaping gauntlet's own interaction type (harness/agent_session.py's `AgentSession.
    _record`, Layer 2 of specs/shaping-eval-design.md): one founder line and the real `claude`
    CLI agent's reply, rendered through the same `_conversation_card` renderer every other
    interaction type already uses -- "instruction" here is repurposed as "what the founder said",
    never a wire instruction (this interaction type carries no `rubric.py` checks at all; it is
    conversation-only evidence, per the design's own "own small parallel roll-up" boundary)."""
    merged = _merge_captured_text(entries)
    founder_line = merged.get("founder_line", "")
    agent_reply = merged.get("agent_reply", "")
    fact_released = merged.get("fact_released", "none")
    return {
        "instruction": {"purpose": "Founder says", "content": founder_line},
        "requirements": [],
        "reply_summary": agent_reply,
        "outcome": "no fact released this turn" if fact_released in ("", "none")
        else f"fact released: {fact_released}",
    }


def _agent_handoff_conversation(entries: list[dict]) -> dict[str, Any]:
    issuance = _first_matching(entries, kind="protocol", name_prefix="get_next")
    body = _response_body(issuance)
    return {
        "instruction": None,
        "requirements": None,
        "reply_summary": None,
        "outcome": body.get("display"),
        "reason": body.get("reason"),
    }


def _title_for(interaction_type: str, entries: list[dict]) -> str:
    if interaction_type == "agent-cycle":
        issuance = _first_matching(entries, kind="protocol", name_prefix="get_next")
        body = _response_body(issuance)
        purpose = (body.get("instruction") or {}).get("purpose")
        action = body.get("action") or "agent action"
        return f"{action}: {purpose}" if purpose else str(action)
    if interaction_type == "agent-handoff":
        issuance = _first_matching(entries, kind="protocol", name_prefix="get_next")
        body = _response_body(issuance)
        reason = body.get("reason") or "handoff"
        display = body.get("display") or ""
        return f"{reason}: {display[:70]}" if display else str(reason)
    # ui-visit / participant-page: the first step's own name is already founder-readable
    # ("founder opens the problem stage card", "participant opens the invitation link").
    return entries[0].get("name", "interaction") if entries else "interaction"


def derive_interactions(entries: list[dict]) -> list[Interaction]:
    """Groups tagged transcript entries (already sorted by `seq`, as harness.evidence._read_
    transcript leaves them) into Interaction objects, in transcript order (first-seen tag id
    wins the group's position).
    """
    groups: dict[str, list[dict]] = {}
    order: list[str] = []
    for entry in entries:
        tag = entry.get("interaction")
        if not tag or not tag.get("id"):
            continue
        iid = tag["id"]
        if iid not in groups:
            groups[iid] = []
            order.append(iid)
        groups[iid].append(entry)

    interactions: list[Interaction] = []
    for iid in order:
        group = groups[iid]
        # retag_interaction rewrites every record sharing an id to the same type, so by the time
        # the transcript is read back from disk every entry in a group agrees; the first is
        # authoritative for the (unlikely) case a rewrite raced a read.
        itype = group[0]["interaction"]["type"]
        conversation = None
        if itype == "agent-cycle":
            conversation = _agent_cycle_conversation(group)
        elif itype == "agent-handoff":
            conversation = _agent_handoff_conversation(group)
        elif itype == "shaping-turn":
            conversation = _shaping_turn_conversation(group)

        screenshots: list[str] = []
        for entry in group:
            screenshots.extend(entry.get("screenshots") or [])

        interactions.append(Interaction(
            id=iid,
            type=itype,
            title=_title_for(itype, group),
            party=group[0].get("party", "stack"),
            step_seqs=[e["seq"] for e in group if "seq" in e],
            screenshots=screenshots,
            conversation=conversation,
            captured_text=_merge_captured_text(group),
            entries=group,
        ))
    return interactions
