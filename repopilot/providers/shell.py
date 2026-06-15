from __future__ import annotations

import os
import shlex
import subprocess
import time
from pathlib import Path

from repopilot.models import CommandResult, EvaluationCase, ProviderMetadata, RunTrace
from repopilot.runtime.repository import repo_diff


class ShellProvider:
    adapter = "shell"

    def __init__(self, name: str, command_template: str, timeout_seconds: int = 300) -> None:
        self.name = name
        self.command_template = command_template
        self.timeout_seconds = timeout_seconds

    @classmethod
    def from_env(cls, name: str, timeout_seconds: int = 300) -> "ShellProvider":
        key = f"REPOPILOT_{name.upper().replace('-', '_')}_COMMAND"
        command_template = os.getenv(key)
        if not command_template:
            raise RuntimeError(
                f"Missing shell provider command. Set {key}, for example: "
                f'{key}=\'my-agent --repo "{{repo}}" --issue "{{issue}}"\''
            )
        return cls(name=name, command_template=command_template, timeout_seconds=timeout_seconds)

    def metadata(self) -> ProviderMetadata:
        return ProviderMetadata(name=self.name, adapter=self.adapter)

    def run(self, repo_path: Path, case: EvaluationCase) -> RunTrace:
        trace = RunTrace(repo_path=repo_path, issue=case.issue)
        command = self._render_command(repo_path, case)
        trace.add("shell_command", "running external provider", command=command)
        result = self._run_command(command, repo_path)
        trace.add("shell_result", "external provider completed", result=result.model_dump())
        diff = repo_diff(repo_path)
        trace.add("diff", "current repository diff", diff=diff)
        if result.exit_code != 0:
            trace.status = "failed"
        else:
            trace.status = "patched" if diff else "failed"
        return trace

    def _render_command(self, repo_path: Path, case: EvaluationCase) -> str:
        return self.command_template.format(
            repo=str(repo_path),
            issue=shlex.quote(case.issue),
            test_command=shlex.quote(" ".join(case.test_command)),
            case_id=case.id,
        )

    def _run_command(self, command: str, repo_path: Path) -> CommandResult:
        start = time.perf_counter()
        proc = subprocess.run(
            command,
            cwd=repo_path,
            shell=True,
            text=True,
            capture_output=True,
            timeout=self.timeout_seconds,
            check=False,
        )
        duration = time.perf_counter() - start
        return CommandResult(
            command=[command],
            cwd=str(repo_path),
            exit_code=proc.returncode,
            stdout=proc.stdout[-12000:],
            stderr=proc.stderr[-12000:],
            duration_seconds=duration,
        )
