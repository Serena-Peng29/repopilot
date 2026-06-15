from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class WizardPaths:
    case_path: Path
    provider_config_path: Path
    json_report_path: Path
    markdown_report_path: Path
    html_report_path: Path


def build_wizard_paths(output_dir: Path, run_name: str) -> WizardPaths:
    safe_name = slugify_run_name(run_name)
    return WizardPaths(
        case_path=output_dir / f"{safe_name}.jsonl",
        provider_config_path=output_dir / f"{safe_name}.providers.json",
        json_report_path=output_dir / f"{safe_name}.report.json",
        markdown_report_path=output_dir / f"{safe_name}.report.md",
        html_report_path=output_dir / f"{safe_name}.report.html",
    )


def slugify_run_name(value: str) -> str:
    slug = re.sub(r"[^a-zA-Z0-9._-]+", "-", value.strip().lower()).strip("-")
    return slug or "wizard-run"


def write_case_file(
    path: Path,
    *,
    case_id: str,
    repo: str,
    issue: str,
    test_command: str,
    timeout_seconds: int,
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "id": case_id,
        "repo": repo,
        "issue": issue,
        "test_command": test_command.split(),
        "timeout_seconds": timeout_seconds,
    }
    path.write_text(json.dumps(payload) + "\n", encoding="utf-8")


def write_provider_config(
    path: Path,
    *,
    provider_choice: str,
    custom_shell_command: str | None = None,
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    provider = provider_spec(provider_choice, custom_shell_command=custom_shell_command)
    path.write_text(json.dumps({"providers": [provider]}, indent=2) + "\n", encoding="utf-8")


def provider_spec(provider_choice: str, custom_shell_command: str | None = None) -> dict:
    if provider_choice == "demo":
        return {"name": "demo", "type": "builtin", "provider": "demo"}
    if provider_choice == "openai":
        return {"name": "openai", "type": "builtin", "provider": "openai"}
    if provider_choice == "codex":
        return {
            "name": "codex",
            "type": "shell",
            "command": (
                'codex -a never exec --sandbox workspace-write --skip-git-repo-check '
                '--ephemeral "Fix this issue: {issue}. Run tests with: {test_command}. '
                'Keep the patch minimal and do not modify tests."'
            ),
        }
    if provider_choice == "shell":
        if not custom_shell_command:
            raise ValueError("custom_shell_command is required for shell provider")
        return {"name": "custom-shell", "type": "shell", "command": custom_shell_command}
    raise ValueError(f"unknown provider choice: {provider_choice}")
