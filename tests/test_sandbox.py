from pathlib import Path

import pytest

from repopilot.runtime.sandbox import CommandRejectedError, Sandbox


def test_sandbox_runs_allowed_command(tmp_path: Path) -> None:
    result = Sandbox(tmp_path).run(["python", "-c", "print('ok')"])

    assert result.exit_code == 0
    assert "ok" in result.stdout


def test_sandbox_rejects_denied_command(tmp_path: Path) -> None:
    with pytest.raises(CommandRejectedError):
        Sandbox(tmp_path).run(["rm", "-rf", "."])


def test_sandbox_rejects_cwd_escape(tmp_path: Path) -> None:
    with pytest.raises(CommandRejectedError):
        Sandbox(tmp_path).run(["python", "-V"], cwd=tmp_path.parent)
