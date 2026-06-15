from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Settings:
    workspace_dir: Path = Path(".repopilot")
    model: str = "gpt-4.1-mini"
    max_iterations: int = 6
    command_timeout_seconds: int = 60
    provider: str = "auto"

    @classmethod
    def from_env(cls) -> "Settings":
        return cls(
            workspace_dir=Path(os.getenv("REPOPILOT_WORKSPACE", ".repopilot")),
            model=os.getenv("REPOPILOT_MODEL", "gpt-4.1-mini"),
            max_iterations=int(os.getenv("REPOPILOT_MAX_ITERATIONS", "6")),
            command_timeout_seconds=int(os.getenv("REPOPILOT_COMMAND_TIMEOUT", "60")),
            provider=os.getenv("REPOPILOT_PROVIDER", "auto"),
        )
