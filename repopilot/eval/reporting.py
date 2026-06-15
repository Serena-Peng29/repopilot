from __future__ import annotations

from repopilot.models import ArenaReport, ProviderRunResult


def render_markdown_report(report: ArenaReport) -> str:
    lines = [
        "# AgentPatchBench Arena Report",
        "",
        "## Summary",
        "",
    ]
    summary = report.summary
    if summary:
        lines.extend(
            [
                f"- Total cases: {report.total_cases}",
                f"- Total runs: {summary.total_runs}",
                f"- Passed: {summary.passed}",
                f"- Pass rate: {summary.pass_rate:.1%}",
                f"- Average latency: {summary.average_latency_seconds:.2f}s",
                "",
                "### Provider Summary",
                "",
                "| Provider | Runs | Passed | Pass Rate | Avg Latency | Avg Changed Lines | High Risk Runs |",
                "| --- | ---: | ---: | ---: | ---: | ---: | ---: |",
            ]
        )
        for provider in summary.provider_summaries:
            lines.append(
                "| "
                f"{provider.provider} | "
                f"{provider.total_runs} | "
                f"{provider.passed} | "
                f"{provider.pass_rate:.1%} | "
                f"{provider.average_latency_seconds:.2f}s | "
                f"{provider.average_changed_lines:.1f} | "
                f"{provider.high_risk_runs} |"
            )
        lines.append("")

    lines.extend(["## Case Results", ""])
    for case in report.cases:
        lines.extend(
            [
                f"### {case.case_id}",
                "",
                f"- Recommended provider: {case.recommended_provider or 'none'}",
                "",
                "| Provider | Adapter | Model | Tests | Risk | Changed Files | Diff | Time | Recommendation |",
                "| --- | --- | --- | --- | --- | ---: | ---: | ---: | --- |",
            ]
        )
        for result in case.results:
            score = result.score
            metadata = result.metadata
            lines.append(
                "| "
                f"{result.provider} | "
                f"{metadata.adapter if metadata else 'unknown'} | "
                f"{metadata.model if metadata and metadata.model else ''} | "
                f"{'pass' if result.passed else 'fail'} | "
                f"{score.risk_level} | "
                f"{score.changed_files} | "
                f"+{score.additions}/-{score.deletions} | "
                f"{result.latency_seconds:.2f}s | "
                f"{result.recommendation} |"
            )
        lines.append("")
        for result in case.results:
            lines.extend(_render_result_details(result))

    return "\n".join(lines).rstrip() + "\n"


def _render_result_details(result: ProviderRunResult) -> list[str]:
    score = result.score
    lines = [
        f"#### {result.provider} Details",
        "",
        f"- Status: {result.status}",
        f"- Trace: `{result.trace_path or 'none'}`",
        f"- Patch: `{result.patch_path or 'none'}`",
        f"- Risk reasons: {', '.join(score.risk_reasons)}",
    ]
    if score.sensitive_files:
        lines.append(f"- Sensitive files: {', '.join(score.sensitive_files)}")
    if score.test_files:
        lines.append(f"- Test files modified: {', '.join(score.test_files)}")
    if result.error:
        lines.append(f"- Error: `{result.error}`")
    lines.append("")
    return lines
