from __future__ import annotations

from repopilot.models import AgentAction, Message, ToolCall
from repopilot.providers.base import AgentProvider


class DemoProvider(AgentProvider):
    """Deterministic provider used for local demos and tests without an API key."""

    name = "demo"
    adapter = "native"

    def __init__(self) -> None:
        self.step = 0
        self.target = "add"

    def next_action(self, messages: list[Message]) -> AgentAction:
        self.step += 1
        transcript = "\n".join(message.content for message in messages[-8:])
        if "multiply" in transcript.lower() or "product" in transcript.lower():
            self.target = "multiply"

        if self.step == 1:
            return AgentAction(
                thought="Inspect the project files to identify a small, relevant repair target.",
                tool_call=ToolCall(name="list_files"),
            )
        if self.step == 2:
            query = "multiply" if self.target == "multiply" else "add"
            return AgentAction(
                thought=f"Search for the relevant arithmetic function: {query}.",
                tool_call=ToolCall(name="search", args={"query": query}),
            )
        if self.step == 3:
            return AgentAction(
                thought="Read the likely implementation file before editing.",
                tool_call=ToolCall(name="read_file", args={"path": "calculator.py"}),
            )
        if self.step == 4 and self.target == "multiply" and "return a + b" in transcript:
            return AgentAction(
                thought="The multiply function adds; replace it with multiplication.",
                tool_call=ToolCall(
                    name="write_file",
                    args={
                        "path": "calculator.py",
                        "content": "def multiply(a: int, b: int) -> int:\n    return a * b\n",
                    },
                ),
            )
        if self.step == 4 and "return a - b" in transcript:
            return AgentAction(
                thought="The add function subtracts; replace it with addition.",
                tool_call=ToolCall(
                    name="write_file",
                    args={
                        "path": "calculator.py",
                        "content": "def add(a: int, b: int) -> int:\n    return a + b\n",
                    },
                ),
            )
        if self.step == 5:
            return AgentAction(
                thought="Run the test suite to verify the patch.",
                tool_call=ToolCall(name="run", args={"command": "python -m pytest -q"}),
            )

        return AgentAction(
            thought="The repair loop has enough evidence to stop.",
            final_answer="Generated a patch and ran the configured verification command.",
        )
