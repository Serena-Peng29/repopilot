from __future__ import annotations

import shutil
from pathlib import Path

from git import Repo


def prepare_repository(source: str, workspace_dir: Path) -> Path:
    workspace_dir.mkdir(parents=True, exist_ok=True)
    if Path(source).exists():
        target = workspace_dir / Path(source).resolve().name
        if target.exists():
            shutil.rmtree(target)
        shutil.copytree(source, target, ignore=shutil.ignore_patterns(".git", ".venv", "__pycache__"))
        Repo.init(target)
        repo = Repo(target)
        repo.index.add(["."])
        repo.index.commit("Initial copied workspace")
        return target

    target = workspace_dir / source.rstrip("/").split("/")[-1].removesuffix(".git")
    if target.exists():
        shutil.rmtree(target)
    Repo.clone_from(source, target)
    return target


def repo_diff(repo_path: Path) -> str:
    repo = Repo(repo_path)
    return repo.git.diff()


def list_project_files(repo_path: Path, limit: int = 250) -> list[str]:
    ignored = {".git", ".venv", "node_modules", "__pycache__", ".pytest_cache"}
    files: list[str] = []
    for path in repo_path.rglob("*"):
        if any(part in ignored for part in path.parts):
            continue
        if path.is_file():
            files.append(str(path.relative_to(repo_path)))
        if len(files) >= limit:
            break
    return sorted(files)
