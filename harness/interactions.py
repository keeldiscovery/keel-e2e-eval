"""Derives scored Interaction objects from a tagged transcript (data-model.md's "Interaction
(derived, harness/interactions.py)"). Pure function of `transcript.jsonl` entries -- no wire
calls, no clock -- so `make report RUN=<dir>` can re-derive interactions (and therefore re-score)
from an old bundle alone (FR-007, SC-004).

spec 005-connect-stack FR-009: the interaction kinds are now `ui_visit`, `agent_turn` (an
inference job observed through the screen -- the frame's own state line, never a wire protocol
call: there is no more founder-agent HTTP/MCP surface for this harness to speak), `participant_
visit`, and `arrival`. The agent-cycle/agent-handoff/agent-refusal/chat-visit/shaping-turn kinds
from the retired agent-protocol harness are gone with it (evals/policy.py's FR-010 removal).

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
    type: str  # ui_visit | agent_turn | participant_visit | arrival | fidelity-summary
    title: str
    party: str
    step_seqs: list[int] = field(default_factory=list)
    screenshots: list[str] = field(default_factory=list)
    conversation: dict[str, Any] | None = None
    captured_text: dict[str, str] = field(default_factory=dict)
    # Not part of data-model.md's serialized shape (scorecard.json only carries id/type/title/
    # attributes/checks) -- kept here so harness/rubric.py can inspect raw step request/response
    # bodies a check needs without re-parsing the transcript itself.
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


def _agent_turn_conversation(entries: list[dict]) -> dict[str, Any]:
    """`agent_turn` (FR-009): the inference job's own turn, observed entirely through the
    screen -- there is no wire protocol call to read a raw instruction/requirements from any
    more (keel-runtime's scripted executor runs the job; the founder only ever sees the frame's
    own state line and the agent's rendered reply). `harness/browser.py`'s `Chat` page object
    stashes these under `chat_state` (the composer's own "Connected · ..." / "Reading what you
    wrote..." line) and `agent_reply` (the bubble text) -- rendered through the same generic
    `_conversation_card` every other interaction type already uses, "instruction" repurposed as
    "what the screen said while waiting", never a wire instruction.
    """
    merged = _merge_captured_text(entries)
    return {
        "instruction": {"purpose": "screen state", "content": merged.get("chat_state", "")},
        "requirements": [],
        "reply_summary": merged.get("agent_reply", ""),
        "outcome": merged.get("agent_turn_outcome", ""),
    }


def _arrival_conversation(entries: list[dict]) -> dict[str, Any]:
    merged = _merge_captured_text(entries)
    return {
        "instruction": None,
        "requirements": None,
        "reply_summary": None,
        "outcome": merged.get("arrival_display", ""),
    }


def _title_for(interaction_type: str, entries: list[dict]) -> str:
    # ui_visit / participant_visit / agent_turn / arrival: the first step's own name is already
    # founder-readable ("founder opens the problem stage card", "participant opens the
    # invitation link", "the agent answers the problem framing").
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
        if itype == "agent_turn":
            conversation = _agent_turn_conversation(group)
        elif itype == "arrival":
            conversation = _arrival_conversation(group)

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
