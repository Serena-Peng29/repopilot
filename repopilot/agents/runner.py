from __future__ import annotations

import shlex
from pathlib import Path

from repopilot.agents.tools import ToolRegistry
from repopilot.config import Settings
from repopilot.models import Message, RunTrace
from repopilot.providers.base import AgentProvider
from repopilot.runtime.repository import repo_diff
from repopilot.runtime.sandbox import Sandbox


class RepoPilotRunner:
    def __init__(self, provider: AgentProvider, settings: Settings) -> None:
        self.provider = provider
        self.settings = settings

    def run(self, repo_path: Path, issue: str, test_command: str | None = None) -> RunTrace:
        trace = RunTrace(repo_path=repo_path, issue=issue)
        sandbox = Sandbox(repo_path, timeout_seconds=self.settings.command_timeout_seconds)
        tools = ToolRegistry(repo_path, sandbox)
        command_hint = f"\nVerification command: {test_command}" if test_command else ""
        messages = [
            Message(
                role="user",
                content=(
                    "Fix this repository issue. Work autonomously with tools, keep edits small, "
                    f"and verify before finishing.{command_hint}\n\nIssue:\n{issue}"
                ),
            )
        ]

        for iteration in range(1, self.settings.max_iterations + 1):
            action = self.provider.next_action(messages)
            trace.add(
                "agent_action",
                action.thought,
                iteration=iteration,
                tool_call=action.tool_call.model_dump() if action.tool_call else None,
                final_answer=action.final_answer,
            )

            if action.tool_call:
                try:
                    output = tools.execute(action.tool_call)
                except Exception as exc:  # noqa: BLE001 - tool errors are part of the trace.
                    output = f"TOOL_ERROR: {type(exc).__name__}: {exc}"
                trace.add("tool_result", action.tool_call.name, output=output[:20000])
                messages.append(Message(role="assistant", content=action.model_dump_json()))
                messages.append(Message(role="tool", content=output))
                continue

            if action.final_answer:
                break

        diff = repo_diff(repo_path)
        trace.add("diff", "current repository diff", diff=diff)
        trace.status = "patched" if diff else "failed"

        if test_command:
            result = sandbox.run(shlex.split(test_command))
            trace.add("verification", test_command, result=result.model_dump())
            trace.status = "tests_passed" if result.exit_code == 0 and diff else "tests_failed"

        return trace
