from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class ProductionStage(str, Enum):
    PLANNED = "planned"
    RUNNING = "running"
    EVALUATING = "evaluating"
    REVISING = "revising"
    APPROVED = "approved"
    RENDERED = "rendered"
    PUBLISHED = "published"
    FAILED = "failed"


@dataclass
class StageResult:
    success: bool
    outputs: dict[str, Any] = field(default_factory=dict)
    error: str | None = None
    retryable: bool = True


@dataclass
class ProductionContext:
    project_id: str
    stage: ProductionStage = ProductionStage.PLANNED
    data: dict[str, Any] = field(default_factory=dict)
    history: list[dict[str, Any]] = field(default_factory=list)
    attempts: dict[str, int] = field(default_factory=dict)

    def record(self, event: str, **payload: Any) -> None:
        self.history.append({"event": event, **payload})

    def increment_attempt(self, stage: ProductionStage) -> int:
        key = stage.value
        self.attempts[key] = self.attempts.get(key, 0) + 1
        return self.attempts[key]
