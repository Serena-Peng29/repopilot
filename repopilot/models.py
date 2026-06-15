from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Literal
from uuid import uuid4

from pydantic import BaseModel, Field


Role = Literal["system", "user", "assistant", "tool"]
PatchStatus = Literal["not_started", "patched", "tests_passed", "tests_failed", "failed"]
RiskLevel = Literal["low", "medium", "high"]


class Message(BaseModel):
    role: Role
    content: str


class ToolCall(BaseModel):
    name: str
    args: dict[str, str] = Field(default_factory=dict)


class AgentAction(BaseModel):
    thought: str
    tool_call: ToolCall | None = None
    final_answer: str | None = None


class CommandResult(BaseModel):
    command: list[str]
    cwd: str
    exit_code: int
    stdout: str
    stderr: str
    duration_seconds: float


class TraceEvent(BaseModel):
    kind: str
    summary: str
    payload: dict = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class RunTrace(BaseModel):
    run_id: str = Field(default_factory=lambda: uuid4().hex)
    repo_path: Path
    issue: str
    status: PatchStatus = "not_started"
    events: list[TraceEvent] = Field(default_factory=list)

    def add(self, kind: str, summary: str, **payload: object) -> None:
        self.events.append(TraceEvent(kind=kind, summary=summary, payload=dict(payload)))


class EvaluationCase(BaseModel):
    id: str
    repo: str
    issue: str
    test_command: list[str]
    expected_files: list[str] = Field(default_factory=list)
    labels: list[str] = Field(default_factory=list)
    timeout_seconds: int | None = None


class ProviderSpec(BaseModel):
    name: str
    type: str = "builtin"
    provider: str | None = None
    command: str | None = None
    model: str | None = None


class ProviderConfig(BaseModel):
    providers: list[ProviderSpec]


class PatchScore(BaseModel):
    changed_files: int = 0
    additions: int = 0
    deletions: int = 0
    sensitive_files: list[str] = Field(default_factory=list)
    test_files: list[str] = Field(default_factory=list)
    risk_level: RiskLevel = "low"
    risk_reasons: list[str] = Field(default_factory=list)


class ProviderMetadata(BaseModel):
    name: str
    adapter: str
    model: str | None = None
    estimated_cost_usd: float | None = None


class ProviderRunResult(BaseModel):
    case_id: str
    provider: str
    metadata: ProviderMetadata | None = None
    status: PatchStatus
    passed: bool
    latency_seconds: float
    trace_path: str
    patch_path: str | None = None
    score: PatchScore
    recommendation: str = "not_selected"
    error: str | None = None


class CaseComparison(BaseModel):
    case_id: str
    recommended_provider: str | None = None
    results: list[ProviderRunResult] = Field(default_factory=list)


class ProviderSummary(BaseModel):
    provider: str
    total_runs: int
    passed: int
    pass_rate: float
    average_latency_seconds: float
    average_changed_lines: float
    high_risk_runs: int


class ArenaSummary(BaseModel):
    total_runs: int
    passed: int
    pass_rate: float
    average_latency_seconds: float
    provider_summaries: list[ProviderSummary] = Field(default_factory=list)


class ArenaReport(BaseModel):
    total_cases: int
    providers: list[str]
    cases: list[CaseComparison]
    summary: ArenaSummary | None = None
