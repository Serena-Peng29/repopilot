import json
from pathlib import Path

from repopilot.wizard import (
    build_wizard_paths,
    provider_spec,
    slugify_run_name,
    write_case_file,
    write_provider_config,
)


def test_slugify_run_name() -> None:
    assert slugify_run_name(" My Repo Fix ") == "my-repo-fix"
    assert slugify_run_name("!!!") == "wizard-run"


def test_build_wizard_paths(tmp_path: Path) -> None:
    paths = build_wizard_paths(tmp_path, "Smoke Test")

    assert paths.case_path == tmp_path / "smoke-test.jsonl"
    assert paths.provider_config_path == tmp_path / "smoke-test.providers.json"
    assert paths.html_report_path == tmp_path / "smoke-test.report.html"


def test_write_case_file(tmp_path: Path) -> None:
    path = tmp_path / "case.jsonl"

    write_case_file(
        path,
        case_id="sample",
        repo=".",
        issue="Fix it",
        test_command="python -m pytest -q",
        timeout_seconds=120,
    )

    payload = json.loads(path.read_text(encoding="utf-8"))
    assert payload["id"] == "sample"
    assert payload["test_command"] == ["python", "-m", "pytest", "-q"]
    assert payload["timeout_seconds"] == 120


def test_provider_spec_codex() -> None:
    spec = provider_spec("codex")

    assert spec["name"] == "codex"
    assert spec["type"] == "shell"
    assert "codex -a never exec" in spec["command"]


def test_write_provider_config_shell(tmp_path: Path) -> None:
    path = tmp_path / "providers.json"

    write_provider_config(
        path,
        provider_choice="shell",
        custom_shell_command='tool --repo "{repo}" --issue {issue}',
    )

    payload = json.loads(path.read_text(encoding="utf-8"))
    assert payload["providers"][0]["name"] == "custom-shell"
    assert payload["providers"][0]["type"] == "shell"
