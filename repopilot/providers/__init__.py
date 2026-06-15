from __future__ import annotations

import os

from repopilot.config import Settings
from repopilot.providers.base import AgentProvider
from repopilot.providers.demo import DemoProvider
from repopilot.providers.openai_provider import OpenAIProvider


def create_provider(settings: Settings) -> AgentProvider:
    if settings.provider == "demo":
        return DemoProvider()
    if settings.provider == "openai":
        return OpenAIProvider(settings.model)
    if os.getenv("OPENAI_API_KEY"):
        return OpenAIProvider(settings.model)
    return DemoProvider()


def is_shell_provider(provider_name: str) -> bool:
    return provider_name.startswith("shell:") or provider_name in {"codex-cli", "claude-code-cli"}


def shell_provider_name(provider_name: str) -> str:
    if provider_name.startswith("shell:"):
        return provider_name.split(":", 1)[1]
    return provider_name
