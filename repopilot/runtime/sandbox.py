from __future__ import annotations

import subprocess
import sys
import time
from pathlib import Path

from repopilot.models import CommandResult


class CommandRejectedError(ValueError):
    pass


class Sandbox:
    """Small command runner with explicit deny rules for local project automation."""

    DENIED_TOKENS = {
        "rm",
        "shutdown",
        "reboot",
        "mkfs",
        "dd",
        "sudo",
        "chmod",
        "chown",
        "curl",
        "wget",
        "ssh",
        "scp",
    }

    def __init__(self, root: Path, timeout_seconds: int = 60) -> None:
        self.root = root.resolve()
        self.timeout_seconds = timeout_seconds

    def run(self, command: list[str], cwd: Path | None = None) -> CommandResult:
        if not command:
            raise CommandRejectedError("empty command")
        if command[0] in self.DENIED_TOKENS:
            raise CommandRejectedError(f"command is not allowed: {command[0]}")
        if command[0] == "python":
            command = [sys.executable, *command[1:]]

        actual_cwd = (cwd or self.root).resolve()
        if self.root not in [actual_cwd, *actual_cwd.parents]:
            raise CommandRejectedError(f"cwd must stay inside sandbox root: {actual_cwd}")

        start = time.perf_counter()
        proc = subprocess.run(
            command,
            cwd=actual_cwd,
            text=True,
            capture_output=True,
            timeout=self.timeout_seconds,
            check=False,
        )
        duration = time.perf_counter() - start
        return CommandResult(
            command=command,
            cwd=str(actual_cwd),
            exit_code=proc.returncode,
            stdout=proc.stdout[-12000:],
            stderr=proc.stderr[-12000:],
            duration_seconds=duration,
        )
