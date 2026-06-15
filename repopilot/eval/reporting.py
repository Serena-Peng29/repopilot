from __future__ import annotations

from html import escape

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


def render_html_report(report: ArenaReport) -> str:
    summary = report.summary
    provider_summary = ""
    if summary:
        provider_rows = "\n".join(
            "<tr>"
            f"<td>{escape(provider.provider)}</td>"
            f"<td>{provider.total_runs}</td>"
            f"<td>{provider.passed}</td>"
            f"<td>{provider.pass_rate:.1%}</td>"
            f"<td>{provider.average_latency_seconds:.2f}s</td>"
            f"<td>{provider.average_changed_lines:.1f}</td>"
            f"<td>{provider.high_risk_runs}</td>"
            "</tr>"
            for provider in summary.provider_summaries
        )
        provider_summary = f"""
        <section>
          <h2>Provider Summary</h2>
          <table>
            <thead>
              <tr>
                <th>Provider</th>
                <th>Runs</th>
                <th>Passed</th>
                <th>Pass Rate</th>
                <th>Avg Latency</th>
                <th>Avg Changed Lines</th>
                <th>High Risk Runs</th>
              </tr>
            </thead>
            <tbody>{provider_rows}</tbody>
          </table>
        </section>
        """

    case_sections = "\n".join(_render_case_html(case) for case in report.cases)
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>AgentPatchBench Arena Report</title>
  <style>
    :root {{
      color-scheme: light;
      --bg: #f7f7f4;
      --panel: #ffffff;
      --text: #202124;
      --muted: #626863;
      --border: #d8ddd6;
      --pass: #0f7a4f;
      --fail: #b42318;
      --low: #0f7a4f;
      --medium: #9a6700;
      --high: #b42318;
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      background: var(--bg);
      color: var(--text);
      font: 14px/1.5 -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
    }}
    main {{
      max-width: 1120px;
      margin: 0 auto;
      padding: 32px 20px 48px;
    }}
    h1, h2, h3 {{ line-height: 1.2; }}
    h1 {{ margin: 0 0 8px; font-size: 32px; }}
    h2 {{ margin-top: 32px; }}
    .muted {{ color: var(--muted); }}
    .cards {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
      gap: 12px;
      margin: 24px 0;
    }}
    .card {{
      background: var(--panel);
      border: 1px solid var(--border);
      border-radius: 8px;
      padding: 16px;
    }}
    .value {{ display: block; font-size: 24px; font-weight: 700; }}
    table {{
      width: 100%;
      border-collapse: collapse;
      background: var(--panel);
      border: 1px solid var(--border);
      border-radius: 8px;
      overflow: hidden;
    }}
    th, td {{
      padding: 10px 12px;
      border-bottom: 1px solid var(--border);
      text-align: left;
      vertical-align: top;
    }}
    th {{ background: #eef1ec; font-weight: 650; }}
    tr:last-child td {{ border-bottom: 0; }}
    code {{
      background: #eef1ec;
      border-radius: 4px;
      padding: 2px 5px;
      word-break: break-all;
    }}
    details {{
      background: var(--panel);
      border: 1px solid var(--border);
      border-radius: 8px;
      padding: 12px 14px;
      margin: 10px 0;
    }}
    summary {{ cursor: pointer; font-weight: 650; }}
    .badge {{
      display: inline-block;
      border-radius: 999px;
      padding: 2px 8px;
      font-size: 12px;
      font-weight: 650;
      background: #eef1ec;
    }}
    .pass {{ color: var(--pass); }}
    .fail {{ color: var(--fail); }}
    .risk-low {{ color: var(--low); }}
    .risk-medium {{ color: var(--medium); }}
    .risk-high {{ color: var(--high); }}
  </style>
</head>
<body>
  <main>
    <h1>AgentPatchBench Arena Report</h1>
    <p class="muted">Static report generated by RepoPilot.</p>
    {_render_summary_cards(report)}
    {provider_summary}
    <section>
      <h2>Case Results</h2>
      {case_sections}
    </section>
  </main>
</body>
</html>
"""


def _render_summary_cards(report: ArenaReport) -> str:
    summary = report.summary
    if not summary:
        return ""
    return f"""
    <section class="cards" aria-label="Summary">
      <div class="card"><span class="muted">Cases</span><span class="value">{report.total_cases}</span></div>
      <div class="card"><span class="muted">Runs</span><span class="value">{summary.total_runs}</span></div>
      <div class="card"><span class="muted">Passed</span><span class="value">{summary.passed}</span></div>
      <div class="card"><span class="muted">Pass Rate</span><span class="value">{summary.pass_rate:.1%}</span></div>
      <div class="card"><span class="muted">Avg Latency</span><span class="value">{summary.average_latency_seconds:.2f}s</span></div>
    </section>
    """


def _render_case_html(case) -> str:
    rows = "\n".join(_render_result_row(result) for result in case.results)
    details = "\n".join(_render_result_details_html(result) for result in case.results)
    return f"""
    <article>
      <h3>{escape(case.case_id)}</h3>
      <p class="muted">Recommended provider: {escape(case.recommended_provider or "none")}</p>
      <table>
        <thead>
          <tr>
            <th>Provider</th>
            <th>Adapter</th>
            <th>Model</th>
            <th>Tests</th>
            <th>Risk</th>
            <th>Files</th>
            <th>Diff</th>
            <th>Time</th>
            <th>Recommendation</th>
          </tr>
        </thead>
        <tbody>{rows}</tbody>
      </table>
      {details}
    </article>
    """


def _render_result_row(result: ProviderRunResult) -> str:
    score = result.score
    metadata = result.metadata
    status_class = "pass" if result.passed else "fail"
    return (
        "<tr>"
        f"<td>{escape(result.provider)}</td>"
        f"<td>{escape(metadata.adapter if metadata else 'unknown')}</td>"
        f"<td>{escape(metadata.model if metadata and metadata.model else '')}</td>"
        f"<td class=\"{status_class}\">{'pass' if result.passed else 'fail'}</td>"
        f"<td class=\"risk-{escape(score.risk_level)}\">{escape(score.risk_level)}</td>"
        f"<td>{score.changed_files}</td>"
        f"<td>+{score.additions}/-{score.deletions}</td>"
        f"<td>{result.latency_seconds:.2f}s</td>"
        f"<td>{escape(result.recommendation)}</td>"
        "</tr>"
    )


def _render_result_details_html(result: ProviderRunResult) -> str:
    score = result.score
    extra = ""
    if score.sensitive_files:
        extra += f"<li>Sensitive files: {escape(', '.join(score.sensitive_files))}</li>"
    if score.test_files:
        extra += f"<li>Test files modified: {escape(', '.join(score.test_files))}</li>"
    if result.error:
        extra += f"<li>Error: <code>{escape(result.error)}</code></li>"
    return f"""
    <details>
      <summary>{escape(result.provider)} details</summary>
      <ul>
        <li>Status: {escape(result.status)}</li>
        <li>Trace: <code>{escape(result.trace_path or 'none')}</code></li>
        <li>Patch: <code>{escape(result.patch_path or 'none')}</code></li>
        <li>Risk reasons: {escape(', '.join(score.risk_reasons))}</li>
        {extra}
      </ul>
    </details>
    """
