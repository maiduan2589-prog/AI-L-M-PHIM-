from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any
from uuid import uuid4

from src.ai_providers import Capability, ProviderGateway, ProviderRequest
from src.artifacts import Artifact, ArtifactStorage, ArtifactType

from .models import GenerationJob


@dataclass(frozen=True)
class GenerationRequest:
    """Production-facing input for one provider generation operation."""

    project_id: str
    stage: str
    capability: Capability
    payload: dict[str, Any]
    input_refs: list[str] = field(default_factory=list)
    provider_id: str | None = None
    artifact_type: ArtifactType = ArtifactType.OTHER
    mime_type: str | None = None


@dataclass(frozen=True)
class GenerationResult:
    """Normalized result containing the job and any persisted artifacts."""

    job: GenerationJob
    artifacts: list[Artifact] = field(default_factory=list)


class GenerationService:
    """Coordinates provider execution, job lifecycle, and artifact persistence."""

    def __init__(self, gateway: ProviderGateway, storage: ArtifactStorage) -> None:
        self._gateway = gateway
        self._storage = storage

    def generate(self, request: GenerationRequest) -> GenerationResult:
        provider_id = request.provider_id or "auto"
        job = GenerationJob(
            id=str(uuid4()),
            project_id=request.project_id,
            stage=request.stage,
            provider=provider_id,
            capability=request.capability,
            input_refs=list(request.input_refs),
        )

        job.mark_running()
        result = self._gateway.generate(
            ProviderRequest(capability=request.capability, payload=request.payload),
            provider_id=request.provider_id,
        )
        if not result.success:
            job.mark_failed(result.error or "Provider generation failed")
            return GenerationResult(job=job)

        artifacts = self._persist_output(result.output, request)
        job.provider = result.provider_id or provider_id
        job.mark_succeeded([artifact.id for artifact in artifacts])
        return GenerationResult(job=job, artifacts=artifacts)

    def _persist_output(self, output: Any, request: GenerationRequest) -> list[Artifact]:
        if output is None:
            return []
        if isinstance(output, Artifact):
            return [output]
        if not isinstance(output, bytes):
            raise TypeError("Provider output must be bytes or Artifact")

        artifact_id = str(uuid4())
        artifact = Artifact(
            id=artifact_id,
            type=request.artifact_type,
            uri=f"artifact://{artifact_id}",
            mime_type=request.mime_type,
            size_bytes=len(output),
        )
        return [self._storage.put(artifact, output)]
