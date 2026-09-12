"""`harness/codex_host.py`'s own readers, against the shapes measured on 2026-09-12 with codex-cli
0.154.0 (keel-runtime spec 008). Nothing here runs the CLI."""
from __future__ import annotations

from harness import codex_host

EVENTS = [
    {"type": "thread.started", "thread_id": "t"},
    {"type": "turn.started"},
    {"type": "item.completed", "item": {"id": "item_0", "type": "agent_message",
                                        "text": "I’m using the keel-connect skill to start the local runtime."}},
    {"type": "item.started", "item": {"id": "item_1", "type": "command_execution",
                                      "command": "/bin/zsh -lc 'cat .agents/skills/keel-connect/SKILL.md'"}},
    {"type": "item.completed", "item": {"id": "item_1", "type": "command_execution",
                                        "command": "/bin/zsh -lc 'cat .agents/skills/keel-connect/SKILL.md'",
                                        "exit_code": 0, "aggregated_output": "---\nname: keel-connect"}},
    {"type": "item.started", "item": {"id": "item_2", "type": "command_execution",
                                      "command": "/bin/zsh -lc 'python3 .agents/skills/keel-connect/scripts/keel_connect_check.py'"}},
    {"type": "item.completed", "item": {"id": "item_2", "type": "command_execution",
                                        "command": "/bin/zsh -lc 'python3 .agents/skills/keel-connect/scripts/keel_connect_check.py'",
                                        "exit_code": 0, "aggregated_output": '{"outcome": "authorization_started"}'}},
    {"type": "item.completed", "item": {"id": "item_3", "type": "agent_message",
                                        "text": "Open the approval page and approve with code **TZYK-PKHY**."}},
    {"type": "turn.completed", "usage": {"input_tokens": 53751, "cached_input_tokens": 43008,
                                          "cache_write_input_tokens": 0, "output_tokens": 158,
                                          "reasoning_output_tokens": 0}},
]


def test_the_reply_is_the_last_agent_message_not_the_first():
    assert codex_host._final_answer(EVENTS).startswith("Open the approval page")
    assert codex_host._final_answer([]) == ""


def test_tools_used_are_the_commands_the_host_ran_in_order_of_first_use():
    run = codex_host.CodexRun(argv=["codex"], exit_code=0, reply_text="", events=EVENTS)
    assert run.tools_used == [
        "command_execution: /bin/zsh -lc 'cat .agents/skills/keel-connect/SKILL.md'",
        "command_execution: /bin/zsh -lc 'python3 .agents/skills/keel-connect/scripts/keel_connect_check.py'",
    ]


def test_spend_is_tokens_and_never_dollars_or_premium_requests():
    run = codex_host.CodexRun(argv=[], exit_code=0, reply_text="", events=EVENTS)
    spend = run.spend()
    assert spend["tokens"]["output_tokens"] == 158
    assert spend["num_turns"] == 1
    assert "total_cost_usd" not in spend and "premium_requests" not in spend
    assert "tokens" in spend["unit"]


def test_the_model_is_the_pin_or_honestly_nothing():
    assert codex_host.CodexRun(argv=[], exit_code=0, reply_text="", events=EVENTS).model is None
    assert codex_host.CodexRun(argv=[], exit_code=0, reply_text="", events=EVENTS,
                               pinned_model="gpt-6-astra").model == "gpt-6-astra"


def test_readiness_refuses_without_the_key_in_the_shell_and_says_what_to_export(monkeypatch):
    monkeypatch.setattr(codex_host.shutil, "which", lambda b: "/fake/bin/codex")
    monkeypatch.setattr(codex_host.subprocess, "run",
                        lambda *a, **k: type("D", (), {"stdout": "codex-cli 0.154.0\n", "stderr": "",
                                                       "returncode": 0})())
    ready = codex_host.readiness(env={"PATH": "/fake/bin"})
    assert ready["ok"] is False
    assert codex_host.API_KEY_ENV in ready["reason"]
    assert ready["version"] == "codex-cli 0.154.0"


def test_readiness_names_a_missing_cli_by_name(monkeypatch):
    monkeypatch.setattr(codex_host.shutil, "which", lambda b: None)
    ready = codex_host.readiness(env={})
    assert ready["ok"] is False and "@openai/codex" in ready["reason"]
