from __future__ import annotations

from dataclasses import dataclass

from repopilot.models import AgentAction, Message, ToolCall
from repopilot.providers.base import AgentProvider


@dataclass(frozen=True)
class DemoRepair:
    keywords: tuple[str, ...]
    query: str
    path: str
    content: str


REPAIRS = (
    DemoRepair(
        keywords=("multiply", "product"),
        query="multiply",
        path="calculator.py",
        content="def multiply(a: int, b: int) -> int:\n    return a * b\n",
    ),
    DemoRepair(
        keywords=("divide", "division"),
        query="divide",
        path="calculator.py",
        content="def divide(a: float, b: float) -> float:\n    return a / b\n",
    ),
    DemoRepair(
        keywords=("slugify", "hyphen", "whitespace"),
        query="slugify",
        path="text_utils.py",
        content=(
            "import re\n\n\n"
            "def slugify(value: str) -> str:\n"
            "    return re.sub(r\"-+\", \"-\", re.sub(r\"\\s+\", \"-\", value.strip().lower()))\n"
        ),
    ),
    DemoRepair(
        keywords=("csv", "comma-separated", "parse_csv_line"),
        query="parse_csv_line",
        path="parser.py",
        content=(
            "def parse_csv_line(line: str) -> list[str]:\n"
            "    return [part.strip() for part in line.split(\",\")]\n"
        ),
    ),
    DemoRepair(
        keywords=("timeout", "default", "get_timeout"),
        query="get_timeout",
        path="config.py",
        content="def get_timeout(config: dict) -> int:\n    return int(config.get(\"timeout\", 30))\n",
    ),
    DemoRepair(
        keywords=("unique_items", "duplicates", "first-seen"),
        query="unique_items",
        path="collections_utils.py",
        content=(
            "def unique_items(items: list[str]) -> list[str]:\n"
            "    seen = set()\n"
            "    result: list[str] = []\n"
            "    for item in items:\n"
            "        if item not in seen:\n"
            "            seen.add(item)\n"
            "            result.append(item)\n"
            "    return result\n"
        ),
    ),
    DemoRepair(
        keywords=("fahrenheit", "celsius", "temperature"),
        query="celsius_to_fahrenheit",
        path="temperature.py",
        content="def celsius_to_fahrenheit(celsius: float) -> float:\n    return celsius * 9 / 5 + 32\n",
    ),
    DemoRepair(
        keywords=("add", "addition"),
        query="add",
        path="calculator.py",
        content="def add(a: int, b: int) -> int:\n    return a + b\n",
    ),
)


class DemoProvider(AgentProvider):
    """Deterministic provider used for local demos and tests without an API key."""

    name = "demo"
    adapter = "native"

    def __init__(self) -> None:
        self.step = 0
        self.repair = REPAIRS[-1]
        self._repair_locked = False

    def next_action(self, messages: list[Message]) -> AgentAction:
        self.step += 1
        transcript = "\n".join(message.content for message in messages[-8:]).lower()
        if not self._repair_locked:
            self.repair = _select_repair(transcript)
            self._repair_locked = True

        if self.step == 1:
            return AgentAction(
                thought="Inspect the project files to identify a small, relevant repair target.",
                tool_call=ToolCall(name="list_files"),
            )
        if self.step == 2:
            return AgentAction(
                thought=f"Search for the relevant implementation: {self.repair.query}.",
                tool_call=ToolCall(name="search", args={"query": self.repair.query}),
            )
        if self.step == 3:
            return AgentAction(
                thought="Read the likely implementation file before editing.",
                tool_call=ToolCall(name="read_file", args={"path": self.repair.path}),
            )
        if self.step == 4:
            return AgentAction(
                thought="Apply the deterministic demo repair for this sample case.",
                tool_call=ToolCall(
                    name="write_file",
                    args={"path": self.repair.path, "content": self.repair.content},
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


def _select_repair(transcript: str) -> DemoRepair:
    for repair in REPAIRS:
        if any(keyword in transcript for keyword in repair.keywords):
            return repair
    return REPAIRS[-1]
