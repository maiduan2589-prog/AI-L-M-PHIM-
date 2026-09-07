from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any

from src.ai_providers import Capability


class GenerationJobStatus(str, Enum):
    QUEUED = "queued"
    RUNNING = "running"
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class GenerationJob:
    """Lifecycle record for one request to an AI provider.

    A job records production-facing references and execution state. It does
    not select providers, call vendor APIs, or store artifact bytes.
    """

    id: str
    project_id: str
    stage: str
    provider: str
    capability: Capability
    input_refs: list[str] = field(default_factory=list)
    output_refs: list[str] = field(default_factory=list)
    status: GenerationJobStatus = GenerationJobStatus.QUEUED
    attempt: int = 0
    error: str | None = None
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    completed_at: datetime | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def mark_running(self) -> None:
        if self.status not in (GenerationJobStatus.QUEUED, GenerationJobStatus.FAILED):
            raise ValueError(f"Cannot run job from status: {self.status.value}")
        self.status = GenerationJobStatus.RUNNING
        self.attempt += 1
        self.error = None
        self.completed_at = None

    def mark_succeeded(self, output_refs: list[str] | None = None) -> None:
        if self.status is not GenerationJobStatus.RUNNING:
            raise ValueError(f"Cannot succeed job from status: {self.status.value}")
        if output_refs is not None:
            self.output_refs = list(output_refs)
        self.status = GenerationJobStatus.SUCCEEDED
        self.completed_at = datetime.now(timezone.utc)

    def mark_failed(self, error: str) -> None:
        if self.status is not GenerationJobStatus.RUNNING:
            raise ValueError(f"Cannot fail job from status: {self.status.value}")
        if not error:
            raise ValueError("error must not be empty")
        self.status = GenerationJobStatus.FAILED
        self.error = error
        self.completed_at = datetime.now(timezone.utc)

    def cancel(self) -> None:
        if self.status not in (GenerationJobStatus.QUEUED, GenerationJobStatus.RUNNING):
            raise ValueError(f"Cannot cancel job from status: {self.status.value}")
        self.status = GenerationJobStatus.CANCELLED
        self.completed_at = datetime.now(timezone.utc)
