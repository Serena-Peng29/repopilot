from __future__ import annotations

import json
from pathlib import Path

from repopilot.agents.runner import RepoPilotRunner
from repopilot.config import Settings
from repopilot.models import EvaluationCase
from repopilot.providers import create_provider
from repopilot.runtime.repository import prepare_repository
from repopilot.trace import save_trace


def load_cases(path: Path) -> list[EvaluationCase]:
    cases = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            cases.append(EvaluationCase.model_validate(json.loads(line)))
    return cases


def run_evaluation(cases_path: Path, settings: Settings) -> dict:
    cases = load_cases(cases_path)
    rows: list[dict] = []
    passed = 0

    for case in cases:
        repo_path = prepare_repository(case.repo, settings.workspace_dir / "eval" / case.id)
        runner = RepoPilotRunner(create_provider(settings), settings)
        trace = runner.run(repo_path, case.issue, test_command=" ".join(case.test_command))
        trace_path = save_trace(trace, settings.workspace_dir / "eval-traces")
        ok = trace.status == "tests_passed"
        passed += int(ok)
        rows.append(
            {
                "id": case.id,
                "status": trace.status,
                "passed": ok,
                "trace_path": str(trace_path),
            }
        )

    return {
        "total": len(cases),
        "passed": passed,
        "pass_rate": passed / len(cases) if cases else 0,
        "cases": rows,
    }
