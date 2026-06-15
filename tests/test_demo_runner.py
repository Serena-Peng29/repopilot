from pathlib import Path

from repopilot.agents.runner import RepoPilotRunner
from repopilot.config import Settings
from repopilot.providers.demo import DemoProvider
from repopilot.runtime.repository import prepare_repository


def test_demo_runner_repairs_sample_project(tmp_path: Path) -> None:
    source = Path("examples/sample_buggy_project")
    repo_path = prepare_repository(str(source), tmp_path / "work")
    runner = RepoPilotRunner(
        DemoProvider(),
        Settings(workspace_dir=tmp_path / "workspace", provider="demo", max_iterations=6),
    )

    trace = runner.run(
        repo_path,
        "The add(a, b) function returns the wrong result.",
        test_command="python -m pytest -q",
    )

    assert trace.status == "tests_passed"
    assert "return a + b" in (repo_path / "calculator.py").read_text(encoding="utf-8")
