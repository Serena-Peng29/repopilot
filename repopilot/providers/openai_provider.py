from __future__ import annotations

import json
import os

from pydantic import ValidationError

from repopilot.models import AgentAction, Message, ProviderMetadata
from repopilot.providers.base import AgentProvider


SYSTEM_INSTRUCTIONS = """You are RepoPilot, a careful software engineering agent.
Return exactly one JSON object matching this schema:
{
  "thought": "brief private-free reasoning summary",
  "tool_call": {"name": "list_files|search|read_file|write_file|run|diff", "args": {...}} | null,
  "final_answer": "summary when finished" | null
}

Rules:
- Prefer small, targeted edits.
- Read files before writing them.
- Run tests after editing.
- Use `run` only for project-local commands such as tests, lint, or typecheck.
- Never ask for secrets.
- Stop with final_answer after tests pass or after explaining the blocker.
"""


class OpenAIProvider(AgentProvider):
    name = "openai"
    adapter = "native"

    def __init__(self, model: str) -> None:
        if not os.getenv("OPENAI_API_KEY"):
            raise RuntimeError("OPENAI_API_KEY is required when using --provider openai.")
        try:
            from openai import OpenAI
        except ImportError as exc:
            raise RuntimeError("Install with `pip install -e '.[openai]'` to use OpenAI.") from exc
        self.client = OpenAI()
        self.model = model

    def metadata(self) -> ProviderMetadata:
        return ProviderMetadata(name=self.name, adapter=self.adapter, model=self.model)

    def next_action(self, messages: list[Message]) -> AgentAction:
        try:
            response = self.client.responses.create(
                model=self.model,
                instructions=SYSTEM_INSTRUCTIONS,
                input=[message.model_dump() for message in messages],
            )
        except Exception as exc:  # noqa: BLE001 - surface SDK/API failures with provider context.
            raise RuntimeError(f"OpenAI provider request failed for model {self.model}: {exc}") from exc

        text = response.output_text
        try:
            payload = json.loads(text)
            return AgentAction.model_validate(payload)
        except json.JSONDecodeError as exc:
            preview = text[:1000]
            raise RuntimeError(
                "OpenAI provider returned non-JSON action output. "
                f"Model={self.model}; preview={preview!r}"
            ) from exc
        except ValidationError as exc:
            preview = text[:1000]
            raise RuntimeError(
                "OpenAI provider returned JSON that does not match AgentAction. "
                f"Model={self.model}; errors={exc.errors()}; preview={preview!r}"
            ) from exc
