"""A minimal MCP (Streamable HTTP transport) client, just enough to call `keel_open_web` -- the
one tool with no HTTP equivalent (`harness/browser.py`'s module docstring; `OpenWebUrls` is
MCP-only). Everything else this repo drives goes over `/v2/agent/**` directly.

**Confirmed live, not assumed from the MCP spec** (probed against this stack, since keel-cloud's
own test suite -- `McpToolsFlowTest` et al. -- calls the tool beans directly and never exercises
the wire format a real client actually sees):

1. `POST /mcp` with a JSON-RPC `initialize` request answers plain `application/json` (not SSE),
   200, and carries the session id in an `Mcp-Session-Id` response header -- every subsequent call
   in the same session must echo that header back.
2. `POST /mcp` with `notifications/initialized` (no `id` -- it's a notification, not a request)
   answers `202` with an empty body.
3. `POST /mcp` with `tools/call` answers `text/event-stream`, chunked -- one `data:` line carrying
   the JSON-RPC response as a JSON string. A tool rejection (`KeelMcpTools`'s `guarded`/
   `McpToolRejection`, per that class's own javadoc) comes back as a *successful* JSON-RPC result
   with `isError: true` and the `{rule, problem, remedy}` triple JSON-encoded inside
   `result.content[0].text` -- never a JSON-RPC protocol-level error and never an HTTP error
   status, so a caller must check `isError`, not the status code, to tell a refusal from a result.

This client speaks exactly that dialect and nothing more -- no resources, no prompts, no
reconnection/resumption machinery the full spec allows for. `evals/test_s007_hostile_wire.py` is
the only caller.
"""

from __future__ import annotations

import json
from typing import Any

import requests

from harness.steps import Recorder


class McpToolError(RuntimeError):
    """A tool call answered with `isError: true` -- the flat `{rule, problem, remedy}` triple,
    JSON-decoded from `result.content[0].text` (see this module's docstring, point 3)."""

    def __init__(self, raw_text: str):
        self.raw_text = raw_text
        try:
            body = json.loads(raw_text)
        except json.JSONDecodeError:
            body = {}
        self.rule = body.get("rule")
        self.problem = body.get("problem")
        self.remedy = body.get("remedy")
        super().__init__(f"MCP tool error rule={self.rule}: {self.problem}")


def _parse_sse_json(text: str) -> dict:
    """Pulls the JSON payload out of a `data:` line in an SSE response body (point 3 above)."""
    for line in text.splitlines():
        line = line.strip()
        if line.startswith("data:"):
            return json.loads(line[len("data:"):].strip())
    raise ValueError(f"no 'data:' line found in SSE body: {text!r}")


class McpClient:
    """One session per instance: `initialize()` once, then any number of `call_tool`s."""

    def __init__(self, base_url: str, recorder: Recorder, session: requests.Session | None = None,
                 *, agent_key: str | None = None):
        self.base_url = base_url.rstrip("/")
        self.recorder = recorder
        self.session = session or requests.Session()
        self._mcp_session_id: str | None = None
        self._next_id = 1
        if agent_key:
            # Founder-experience round 2: /mcp sits behind the same X-Keel-Agent-Key gate as
            # /v2/agent/** (AgentKeyAuthorizationManager) -- set once as a session default.
            self.session.headers.update({"X-Keel-Agent-Key": agent_key})

    def _headers(self) -> dict[str, str]:
        headers = {"Content-Type": "application/json", "Accept": "application/json, text/event-stream"}
        if self._mcp_session_id:
            headers["Mcp-Session-Id"] = self._mcp_session_id
        return headers

    def initialize(self) -> dict:
        body = {
            "jsonrpc": "2.0", "id": self._next_id, "method": "initialize",
            "params": {"protocolVersion": "2024-11-05", "capabilities": {},
                       "clientInfo": {"name": "keel-e2e-eval", "version": "0.0.1"}},
        }
        self._next_id += 1
        with self.recorder.step("mcp initialize", party="agent", kind="protocol") as h:
            response = self.session.post(f"{self.base_url}/mcp", json=body, headers=self._headers(), timeout=15)
            self._mcp_session_id = response.headers.get("Mcp-Session-Id")
            parsed = response.json() if response.content else {}
            h.record_wire(body, {"status": response.status_code, "body": parsed,
                                  "mcp_session_id": self._mcp_session_id})
            if response.status_code >= 400 or not self._mcp_session_id:
                h.fail(f"initialize failed: HTTP {response.status_code}, session_id={self._mcp_session_id}")
                raise RuntimeError(h.error)

        notify = {"jsonrpc": "2.0", "method": "notifications/initialized"}
        with self.recorder.step("mcp notifications/initialized", party="agent", kind="protocol") as h:
            response = self.session.post(f"{self.base_url}/mcp", json=notify, headers=self._headers(), timeout=15)
            h.record_wire(notify, {"status": response.status_code})
            if response.status_code >= 300:
                h.fail(f"notifications/initialized failed: HTTP {response.status_code}")
                raise RuntimeError(h.error)
        return parsed

    def call_tool(self, name: str, arguments: dict[str, Any]) -> Any:
        """Returns the tool's own result content (parsed JSON if it looks like JSON, else raw
        text) on success. Raises `McpToolError` on `isError: true` -- the caller reads
        `.rule`/`.problem`/`.remedy`, exactly the shape `AgentDtos.ErrorBody`/`ProtocolError` use
        over HTTP (design: one rejection shape, two transports)."""
        body = {"jsonrpc": "2.0", "id": self._next_id, "method": "tools/call",
                "params": {"name": name, "arguments": arguments}}
        self._next_id += 1
        with self.recorder.step(f"mcp tools/call({name})", party="agent", kind="protocol") as h:
            response = self.session.post(f"{self.base_url}/mcp", json=body, headers=self._headers(), timeout=15)
            raw_body = response.text
            try:
                parsed = _parse_sse_json(raw_body) if "text/event-stream" in response.headers.get(
                    "Content-Type", "") else response.json()
            except (ValueError, json.JSONDecodeError):
                parsed = {"_raw": raw_body}
            h.record_wire(body, {"status": response.status_code, "body": parsed})
            if response.status_code >= 400:
                h.fail(f"tools/call transport error: HTTP {response.status_code}: {parsed}")
                raise RuntimeError(h.error)

            result = (parsed.get("result") or {})
            content = result.get("content") or []
            text = content[0].get("text") if content and isinstance(content[0], dict) else None
            if result.get("isError"):
                h.fail(f"tool refused: {text}")
                error = McpToolError(text or "")
                raise error
            if text is None:
                return result
            try:
                return json.loads(text)
            except (TypeError, json.JSONDecodeError):
                return text
