from __future__ import annotations

from typing import Protocol

from .models import GenerationJob


class GenerationJobRepository(Protocol):
    """Persistence boundary for generation job state."""

    def save(self, job: GenerationJob) -> GenerationJob:
        """Persist the current job state and return the stored job."""
        ...

    def get(self, job_id: str) -> GenerationJob | None:
        """Return a job by id, or None when it does not exist."""
        ...


class InMemoryGenerationJobRepository:
    """Small deterministic repository for local execution and unit tests."""

    def __init__(self) -> None:
        self._jobs: dict[str, GenerationJob] = {}

    def save(self, job: GenerationJob) -> GenerationJob:
        self._jobs[job.id] = job
        return job

    def get(self, job_id: str) -> GenerationJob | None:
        return self._jobs.get(job_id)
