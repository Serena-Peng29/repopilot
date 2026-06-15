from __future__ import annotations

import json
from pathlib import Path

from repopilot.models import RunTrace


def save_trace(trace: RunTrace, output_dir: Path) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    path = output_dir / f"{trace.run_id}.json"
    path.write_text(trace.model_dump_json(indent=2), encoding="utf-8")
    return path


def load_trace(path: Path) -> RunTrace:
    return RunTrace.model_validate(json.loads(path.read_text(encoding="utf-8")))
