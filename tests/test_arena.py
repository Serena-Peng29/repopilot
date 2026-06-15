from pathlib import Path

from repopilot.config import Settings
from repopilot.eval.arena import run_arena, run_arena_with_specs
from repopilot.eval.provider_config import load_provider_config
from repopilot.eval.reporting import render_markdown_report


def test_arena_runs_demo_provider(tmp_path: Path) -> None:
    settings = Settings(workspace_dir=tmp_path / "workspace", provider="demo", max_iterations=6)

    report = run_arena(Path("examples/eval_cases.jsonl"), ["demo"], settings)

    assert report.total_cases == 8
    assert report.providers == ["demo"]
    assert report.summary is not None
    assert report.summary.total_runs == 8
    assert report.summary.passed == 8
    assert report.summary.pass_rate == 1
    case = report.cases[0]
    assert case.recommended_provider == "demo"
    result = case.results[0]
    assert result.provider == "demo"
    assert result.metadata is not None
    assert result.metadata.adapter == "native"
    assert result.passed is True
    assert result.status == "tests_passed"
    assert result.score.risk_level == "low"
    assert result.score.changed_files == 1
    assert result.patch_path is not None
    assert Path(result.patch_path).exists()
    assert Path(result.trace_path).exists()


def test_markdown_report_includes_summary(tmp_path: Path) -> None:
    settings = Settings(workspace_dir=tmp_path / "workspace", provider="demo", max_iterations=6)
    report = run_arena(Path("examples/eval_cases.jsonl"), ["demo"], settings)

    markdown = render_markdown_report(report)

    assert "# AgentPatchBench Arena Report" in markdown
    assert "Pass rate: 100.0%" in markdown
    assert "| demo | native |" in markdown
    assert "sample-addition-bug" in markdown
    assert "sample-multiply-bug" in markdown
    assert "sample-slugify-bug" in markdown


def test_arena_runs_shell_provider(tmp_path: Path, monkeypatch) -> None:
    cases_path = tmp_path / "cases.jsonl"
    cases_path.write_text(
        '{"id":"shell-addition-bug","repo":"examples/sample_buggy_project",'
        '"issue":"The add function subtracts instead of adding.",'
        '"test_command":["python","-m","pytest","-q"]}\n',
        encoding="utf-8",
    )
    command = (
        'python -c "from pathlib import Path; '
        "Path('calculator.py').write_text('def add(a: int, b: int) -> int:\\\\n"
        "    return a + b\\\\n', encoding='utf-8')\""
    )
    monkeypatch.setenv("REPOPILOT_PATCHER_COMMAND", command)
    settings = Settings(workspace_dir=tmp_path / "workspace", provider="demo", max_iterations=6)

    report = run_arena(cases_path, ["shell:patcher"], settings)

    result = report.cases[0].results[0]
    assert result.provider == "shell:patcher"
    assert result.metadata is not None
    assert result.metadata.adapter == "shell"
    assert result.passed is True
    assert result.patch_path is not None


def test_arena_runs_provider_config_demo(tmp_path: Path) -> None:
    settings = Settings(workspace_dir=tmp_path / "workspace", provider="demo", max_iterations=6)
    specs = load_provider_config(Path("examples/providers.demo.json"))

    report = run_arena_with_specs(Path("examples/eval_cases.jsonl"), specs, settings)

    assert report.providers == ["demo"]
    assert report.summary is not None
    assert report.summary.passed == 8


def test_arena_runs_provider_config_shell(tmp_path: Path) -> None:
    cases_path = tmp_path / "cases.jsonl"
    config_path = tmp_path / "providers.json"
    cases_path.write_text(
        '{"id":"shell-addition-bug","repo":"examples/sample_buggy_project",'
        '"issue":"The add function subtracts instead of adding.",'
        '"test_command":["python","-m","pytest","-q"]}\n',
        encoding="utf-8",
    )
    config_path.write_text(
        "{"
        '"providers": ['
        '{"name": "patcher", "type": "shell", '
        '"command": "python -c \\"from pathlib import Path; '
        "Path('calculator.py').write_text('def add(a: int, b: int) -> int:\\\\\\\\n"
        "    return a + b\\\\\\\\n', encoding='utf-8')\\\"\"}"
        "]"
        "}",
        encoding="utf-8",
    )
    settings = Settings(workspace_dir=tmp_path / "workspace", provider="demo", max_iterations=6)
    specs = load_provider_config(config_path)

    report = run_arena_with_specs(cases_path, specs, settings)

    result = report.cases[0].results[0]
    assert result.provider == "patcher"
    assert result.metadata is not None
    assert result.metadata.adapter == "shell"
    assert result.passed is True
