from __future__ import annotations

import json
from pathlib import Path

import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from repopilot.agents.runner import RepoPilotRunner
from repopilot.config import Settings
from repopilot.eval.arena import run_arena, run_arena_with_specs
from repopilot.eval.harness import run_evaluation
from repopilot.eval.provider_config import load_provider_config
from repopilot.eval.reporting import render_markdown_report
from repopilot.providers import create_provider
from repopilot.runtime.repository import prepare_repository
from repopilot.trace import save_trace

app = typer.Typer(help="RepoPilot: turn repository issues into tested patches.")
console = Console()


def solve_issue(
    repo: str,
    issue: str,
    test: str | None,
    provider: str,
    output: Path,
    patch_output: Path | None = None,
) -> None:
    settings = Settings.from_env()
    settings = Settings(
        workspace_dir=settings.workspace_dir,
        model=settings.model,
        max_iterations=settings.max_iterations,
        command_timeout_seconds=settings.command_timeout_seconds,
        provider=provider,
    )
    repo_path = prepare_repository(repo, settings.workspace_dir)
    runner = RepoPilotRunner(create_provider(settings), settings)
    trace = runner.run(repo_path, issue, test_command=test)
    trace_path = save_trace(trace, output)
    diff = next(
        (event.payload.get("diff", "") for event in reversed(trace.events) if event.kind == "diff"),
        "",
    )
    if patch_output and diff:
        patch_output.parent.mkdir(parents=True, exist_ok=True)
        patch_output.write_text(str(diff), encoding="utf-8")

    console.print(Panel.fit(f"Status: [bold]{trace.status}[/bold]\nTrace: {trace_path}"))
    for event in trace.events:
        if event.kind in {"agent_action", "verification", "diff"}:
            console.print(f"[bold]{event.kind}[/bold] {event.summary}")
    console.print(f"\nWorkspace repo: [cyan]{repo_path}[/cyan]")
    if patch_output and diff:
        console.print(f"Patch: [cyan]{patch_output}[/cyan]")


@app.command()
def solve(
    repo: str = typer.Argument(..., help="Local repository path or Git URL."),
    issue: str = typer.Option(..., "--issue", "-i", help="Bug report or issue text."),
    test: str | None = typer.Option(None, "--test", "-t", help="Verification command."),
    provider: str = typer.Option("auto", "--provider", help="auto, demo, or openai."),
    output: Path = typer.Option(Path(".repopilot/traces"), "--output", "-o"),
    patch_output: Path | None = typer.Option(None, "--patch-output", help="Write git diff patch."),
) -> None:
    """Run RepoPilot against one repository issue."""
    solve_issue(repo, issue, test, provider, output, patch_output)


@app.command()
def eval(
    cases: Path = typer.Argument(..., help="JSONL evaluation file."),
    provider: str = typer.Option("demo", "--provider"),
    output: Path = typer.Option(Path(".repopilot/eval-results.json"), "--output", "-o"),
) -> None:
    """Run a small SWE-bench-style evaluation set."""
    settings = Settings.from_env()
    settings = Settings(
        workspace_dir=settings.workspace_dir,
        model=settings.model,
        max_iterations=settings.max_iterations,
        command_timeout_seconds=settings.command_timeout_seconds,
        provider=provider,
    )
    results = run_evaluation(cases, settings)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(results, indent=2), encoding="utf-8")

    table = Table(title="RepoPilot Evaluation")
    table.add_column("Case")
    table.add_column("Status")
    table.add_column("Trace")
    for result in results["cases"]:
        table.add_row(result["id"], result["status"], result["trace_path"])
    console.print(table)
    console.print(f"Pass rate: {results['pass_rate']:.1%}")


@app.command()
def arena(
    cases: Path = typer.Argument(..., help="JSONL evaluation file."),
    providers: str = typer.Option("demo", "--providers", help="Comma-separated provider names."),
    provider_config: Path | None = typer.Option(None, "--provider-config", help="JSON provider config."),
    output: Path = typer.Option(Path(".repopilot/arena-report.json"), "--output", "-o"),
    markdown_report: Path | None = typer.Option(None, "--report", help="Write a Markdown report."),
) -> None:
    """Compare multiple providers on the same benchmark cases."""
    settings = Settings.from_env()
    if provider_config:
        provider_specs = load_provider_config(provider_config)
        if not provider_specs:
            raise typer.BadParameter("Provider config must include at least one provider.")
        report = run_arena_with_specs(cases, provider_specs, settings)
    else:
        provider_names = [provider.strip() for provider in providers.split(",") if provider.strip()]
        if not provider_names:
            raise typer.BadParameter("At least one provider is required.")
        report = run_arena(cases, provider_names, settings)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(report.model_dump_json(indent=2), encoding="utf-8")
    if markdown_report:
        markdown_report.parent.mkdir(parents=True, exist_ok=True)
        markdown_report.write_text(render_markdown_report(report), encoding="utf-8")

    table = Table(title="AgentPatchBench Arena")
    table.add_column("Case")
    table.add_column("Provider")
    table.add_column("Adapter")
    table.add_column("Tests")
    table.add_column("Risk")
    table.add_column("Files")
    table.add_column("Diff")
    table.add_column("Time")
    table.add_column("Reasons")
    table.add_column("Recommendation")

    for case in report.cases:
        for result in case.results:
            score = result.score
            metadata = result.metadata
            tests = "pass" if result.passed else "fail"
            table.add_row(
                case.case_id,
                result.provider,
                metadata.adapter if metadata else "unknown",
                tests,
                score.risk_level,
                str(score.changed_files),
                f"+{score.additions}/-{score.deletions}",
                f"{result.latency_seconds:.2f}s",
                _summarize_reasons(score.risk_reasons),
                result.recommendation,
            )

    console.print(table)
    if report.summary:
        console.print(
            f"Pass rate: [bold]{report.summary.pass_rate:.1%}[/bold] "
            f"({report.summary.passed}/{report.summary.total_runs})"
    )
    console.print(f"Report: [cyan]{output}[/cyan]")
    if markdown_report:
        console.print(f"Markdown: [cyan]{markdown_report}[/cyan]")


@app.command()
def demo() -> None:
    """Run the bundled deterministic demo."""
    sample = Path("examples/sample_buggy_project")
    issue = "The add(a, b) function returns the wrong result for positive numbers."
    solve_issue(
        str(sample),
        issue=issue,
        test="python -m pytest -q",
        provider="demo",
        output=Path(".repopilot/traces"),
        patch_output=Path(".repopilot/demo.patch"),
    )


def _summarize_reasons(reasons: list[str]) -> str:
    if not reasons:
        return ""
    if reasons == ["small focused patch"]:
        return "focused"
    return ", ".join(reasons[:2])


if __name__ == "__main__":
    app()
