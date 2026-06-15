from __future__ import annotations

from unidiff import PatchSet

from repopilot.models import PatchScore, RiskLevel


HIGH_SENSITIVE_PATTERNS = (
    ".env",
    "secret",
    "secrets",
    "credential",
    "credentials",
    "auth",
    "payment",
    "billing",
)

DEPENDENCY_PATTERNS = (
    "requirements.txt",
    "pyproject.toml",
    "poetry.lock",
    "package.json",
    "package-lock.json",
    "pnpm-lock.yaml",
    "yarn.lock",
    "go.mod",
    "go.sum",
    "cargo.toml",
    "cargo.lock",
    "gemfile",
    "gemfile.lock",
)

CI_PATTERNS = (
    ".github/workflows",
    ".gitlab-ci",
    "circleci",
    "buildkite",
    "jenkinsfile",
)

MIGRATION_PATTERNS = (
    "migration",
    "migrations",
)

TEST_PATTERNS = (
    "test_",
    "_test.",
    ".test.",
    ".spec.",
    "/tests/",
    "tests/",
    "__tests__",
)

TEST_WEAKENING_PATTERNS = (
    "skip(",
    "xfail",
    "assert true",
    "assert 1",
    "return",
    "pass",
    "todo",
)


def score_patch(diff: str) -> PatchScore:
    if not diff.strip():
        return PatchScore(risk_level="high", risk_reasons=["no patch was produced"])

    patch = PatchSet(diff)
    changed_paths: list[str] = []
    sensitive_files: list[str] = []
    test_files: list[str] = []
    dependency_files: list[str] = []
    ci_files: list[str] = []
    migration_files: list[str] = []
    test_weakening_hits: list[str] = []
    additions = 0
    deletions = 0

    for patched_file in patch:
        path = patched_file.path
        changed_paths.append(path)
        lowered = path.lower()
        is_test_file = any(pattern in lowered for pattern in TEST_PATTERNS)
        if any(pattern in lowered for pattern in HIGH_SENSITIVE_PATTERNS):
            sensitive_files.append(path)
        if any(pattern in lowered for pattern in DEPENDENCY_PATTERNS):
            dependency_files.append(path)
        if any(pattern in lowered for pattern in CI_PATTERNS):
            ci_files.append(path)
        if any(pattern in lowered for pattern in MIGRATION_PATTERNS):
            migration_files.append(path)
        if is_test_file:
            test_files.append(path)
        for hunk in patched_file:
            for line in hunk:
                if line.is_added:
                    additions += 1
                    if is_test_file and _looks_like_test_weakening(line.value):
                        test_weakening_hits.append(path)
                elif line.is_removed:
                    deletions += 1

    risk_reasons: list[str] = []
    if sensitive_files:
        risk_reasons.append("touches high-sensitivity files")
    if dependency_files:
        risk_reasons.append("changes dependency files")
    if ci_files:
        risk_reasons.append("changes CI configuration")
    if migration_files:
        risk_reasons.append("changes database migrations")
    if test_files:
        risk_reasons.append("modifies test files")
    if test_weakening_hits:
        risk_reasons.append("possible test weakening")
    if len(changed_paths) > 5:
        risk_reasons.append("changes more than five files")
    if additions + deletions > 200:
        risk_reasons.append("large patch over 200 changed lines")

    risk_level = _risk_level(risk_reasons, changed_files=len(changed_paths), changed_lines=additions + deletions)
    if not risk_reasons:
        risk_reasons.append("small focused patch")

    return PatchScore(
        changed_files=len(changed_paths),
        additions=additions,
        deletions=deletions,
        sensitive_files=sensitive_files,
        test_files=test_files,
        risk_level=risk_level,
        risk_reasons=risk_reasons,
    )


def _risk_level(risk_reasons: list[str], changed_files: int, changed_lines: int) -> RiskLevel:
    high_risk_reasons = {
        "touches high-sensitivity files",
        "changes database migrations",
        "possible test weakening",
    }
    if high_risk_reasons.intersection(risk_reasons) or changed_files > 10 or changed_lines > 500:
        return "high"
    if risk_reasons or changed_files > 3 or changed_lines > 100:
        return "medium"
    return "low"


def _looks_like_test_weakening(line: str) -> bool:
    lowered = line.strip().lower()
    if not lowered:
        return False
    if lowered.startswith("#") and "assert" in lowered:
        return True
    if lowered.startswith("#"):
        return False
    if "pytest.mark.skip" in lowered or "pytest.skip" in lowered:
        return True
    if "unittest.skip" in lowered:
        return True
    if any(pattern in lowered for pattern in TEST_WEAKENING_PATTERNS):
        return True
    return False
