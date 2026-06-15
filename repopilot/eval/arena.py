from __future__ import annotations

import time
from pathlib import Path

from repopilot.agents.runner import RepoPilotRunner
from repopilot.config import Settings
from repopilot.eval.harness import load_cases
from repopilot.eval.provider_config import provider_specs_from_names
from repopilot.eval.scoring import score_patch
from repopilot.models import (
    ArenaReport,
    ArenaSummary,
    CaseComparison,
    EvaluationCase,
    ProviderSpec,
    ProviderRunResult,
    ProviderSummary,
)
from repopilot.providers import create_provider
from repopilot.providers.shell import ShellProvider
from repopilot.runtime.repository import prepare_repository
from repopilot.runtime.sandbox import Sandbox
from repopilot.trace import save_trace


def run_arena(cases_path: Path, provider_names: list[str], settings: Settings) -> ArenaReport:
    return run_arena_with_specs(cases_path, provider_specs_from_names(provider_names), settings)


def run_arena_with_specs(
    cases_path: Path,
    provider_specs: list[ProviderSpec],
    settings: Settings,
) -> ArenaReport:
    cases = load_cases(cases_path)
    comparisons = [_run_case(case, provider_specs, settings) for case in cases]
    provider_names = [spec.name for spec in provider_specs]
    return ArenaReport(
        total_cases=len(cases),
        providers=provider_names,
        cases=comparisons,
        summary=_summarize(comparisons, provider_names),
    )


def _run_case(
    case: EvaluationCase,
    provider_specs: list[ProviderSpec],
    settings: Settings,
) -> CaseComparison:
    results = [_run_provider(case, provider_spec, settings) for provider_spec in provider_specs]
    recommended = _recommend(results)

    for result in results:
        if result.provider == recommended:
            result.recommendation = "best"
        elif result.passed:
            result.recommendation = "ok"

    return CaseComparison(case_id=case.id, recommended_provider=recommended, results=results)


def _run_provider(
    case: EvaluationCase,
    provider_spec: ProviderSpec,
    settings: Settings,
) -> ProviderRunResult:
    provider_name = provider_spec.name
    workspace = settings.workspace_dir / "arena" / case.id / provider_name
    traces_dir = settings.workspace_dir / "arena-traces" / case.id / provider_name
    patches_dir = settings.workspace_dir / "arena-patches" / case.id
    test_command = " ".join(case.test_command)
    provider_settings = Settings(
        workspace_dir=settings.workspace_dir,
        model=settings.model,
        max_iterations=settings.max_iterations,
        command_timeout_seconds=case.timeout_seconds or settings.command_timeout_seconds,
        provider=provider_name,
    )

    start = time.perf_counter()
    patch_path: Path | None = None
    try:
        repo_path = prepare_repository(case.repo, workspace)
        if provider_spec.type == "shell":
            provider = _create_shell_provider(provider_spec, provider_settings)
            trace = provider.run(repo_path, case)
            if trace.status == "patched":
                verification = Sandbox(
                    repo_path,
                    timeout_seconds=provider_settings.command_timeout_seconds,
                ).run(case.test_command)
                trace.add("verification", test_command, result=verification.model_dump())
                trace.status = "tests_passed" if verification.exit_code == 0 else "tests_failed"
            metadata = provider.metadata()
        else:
            provider_settings = _settings_for_builtin(provider_spec, provider_settings)
            provider = create_provider(provider_settings)
            runner = RepoPilotRunner(provider, provider_settings)
            trace = runner.run(repo_path, case.issue, test_command=test_command)
            metadata = provider.metadata()
        latency = time.perf_counter() - start
        trace_path = save_trace(trace, traces_dir)
        diff = _extract_diff(trace)
        score = score_patch(diff)
        if diff:
            patches_dir.mkdir(parents=True, exist_ok=True)
            patch_path = patches_dir / f"{provider_name}.patch"
            patch_path.write_text(diff, encoding="utf-8")
        return ProviderRunResult(
            case_id=case.id,
            provider=provider_name,
            metadata=metadata,
            status=trace.status,
            passed=trace.status == "tests_passed",
            latency_seconds=latency,
            trace_path=str(trace_path),
            patch_path=str(patch_path) if patch_path else None,
            score=score,
        )
    except Exception as exc:  # noqa: BLE001 - provider failures are first-class arena results.
        latency = time.perf_counter() - start
        return ProviderRunResult(
            case_id=case.id,
            provider=provider_name,
            metadata=None,
            status="failed",
            passed=False,
            latency_seconds=latency,
            trace_path="",
            patch_path=None,
            score=score_patch(""),
            error=f"{type(exc).__name__}: {exc}",
        )


def _extract_diff(trace) -> str:
    for event in reversed(trace.events):
        if event.kind == "diff":
            return str(event.payload.get("diff", ""))
    return ""


def _recommend(results: list[ProviderRunResult]) -> str | None:
    passing = [result for result in results if result.passed]
    if not passing:
        return None
    risk_rank = {"low": 0, "medium": 1, "high": 2}
    best = min(
        passing,
        key=lambda result: (
            risk_rank[result.score.risk_level],
            result.score.additions + result.score.deletions,
            result.score.changed_files,
            result.latency_seconds,
        ),
    )
    return best.provider


def _summarize(comparisons: list[CaseComparison], provider_names: list[str]) -> ArenaSummary:
    all_results = [result for comparison in comparisons for result in comparison.results]
    passed = sum(1 for result in all_results if result.passed)
    provider_summaries = [
        _summarize_provider(provider_name, all_results) for provider_name in provider_names
    ]
    return ArenaSummary(
        total_runs=len(all_results),
        passed=passed,
        pass_rate=passed / len(all_results) if all_results else 0,
        average_latency_seconds=_average(result.latency_seconds for result in all_results),
        provider_summaries=provider_summaries,
    )


def _summarize_provider(provider_name: str, results: list[ProviderRunResult]) -> ProviderSummary:
    provider_results = [result for result in results if result.provider == provider_name]
    passed = sum(1 for result in provider_results if result.passed)
    return ProviderSummary(
        provider=provider_name,
        total_runs=len(provider_results),
        passed=passed,
        pass_rate=passed / len(provider_results) if provider_results else 0,
        average_latency_seconds=_average(result.latency_seconds for result in provider_results),
        average_changed_lines=_average(
            result.score.additions + result.score.deletions for result in provider_results
        ),
        high_risk_runs=sum(1 for result in provider_results if result.score.risk_level == "high"),
    )


def _average(values) -> float:
    collected = list(values)
    return sum(collected) / len(collected) if collected else 0


def _create_shell_provider(provider_spec: ProviderSpec, settings: Settings) -> ShellProvider:
    shell_name = provider_spec.provider or provider_spec.name.removeprefix("shell:")
    if provider_spec.command:
        return ShellProvider(
            name=provider_spec.name,
            command_template=provider_spec.command,
            timeout_seconds=settings.command_timeout_seconds,
        )
    return ShellProvider.from_env(shell_name, timeout_seconds=settings.command_timeout_seconds)


def _settings_for_builtin(provider_spec: ProviderSpec, settings: Settings) -> Settings:
    return Settings(
        workspace_dir=settings.workspace_dir,
        model=provider_spec.model or settings.model,
        max_iterations=settings.max_iterations,
        command_timeout_seconds=settings.command_timeout_seconds,
        provider=provider_spec.provider or provider_spec.name,
    )
