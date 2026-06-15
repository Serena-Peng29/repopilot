from __future__ import annotations

import shlex
from pathlib import Path

from repopilot.models import ToolCall
from repopilot.runtime.repository import list_project_files, repo_diff
from repopilot.runtime.sandbox import Sandbox


class ToolRegistry:
    def __init__(self, repo_path: Path, sandbox: Sandbox) -> None:
        self.repo_path = repo_path.resolve()
        self.sandbox = sandbox

    def execute(self, call: ToolCall) -> str:
        if call.name == "list_files":
            return "\n".join(list_project_files(self.repo_path))
        if call.name == "search":
            return self._search(call.args.get("query", ""))
        if call.name == "read_file":
            return self._read_file(call.args["path"])
        if call.name == "write_file":
            self._write_file(call.args["path"], call.args["content"])
            return f"wrote {call.args['path']}"
        if call.name == "run":
            command = shlex.split(call.args["command"])
            result = self.sandbox.run(command)
            return result.model_dump_json(indent=2)
        if call.name == "diff":
            return repo_diff(self.repo_path)
        raise ValueError(f"unknown tool: {call.name}")

    def _safe_path(self, relative: str) -> Path:
        path = (self.repo_path / relative).resolve()
        if self.repo_path not in [path, *path.parents]:
            raise ValueError(f"path escapes repository: {relative}")
        return path

    def _read_file(self, relative: str) -> str:
        path = self._safe_path(relative)
        return path.read_text(encoding="utf-8")[:20000]

    def _write_file(self, relative: str, content: str) -> None:
        path = self._safe_path(relative)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")

    def _search(self, query: str) -> str:
        if not query.strip():
            return "empty query"
        matches: list[str] = []
        for file in list_project_files(self.repo_path, limit=400):
            path = self.repo_path / file
            try:
                text = path.read_text(encoding="utf-8")
            except UnicodeDecodeError:
                continue
            for number, line in enumerate(text.splitlines(), start=1):
                if query.lower() in line.lower():
                    matches.append(f"{file}:{number}: {line}")
                    if len(matches) >= 80:
                        return "\n".join(matches)
        return "\n".join(matches) if matches else "no matches"
