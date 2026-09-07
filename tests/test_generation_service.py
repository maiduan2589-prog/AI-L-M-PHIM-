from dataclasses import dataclass

from src.ai_providers import (
    Capability,
    ProviderGateway,
    ProviderMetadata,
    ProviderRegistry,
    ProviderRequest,
    ProviderResult,
)
from src.artifacts import Artifact, ArtifactStorage, ArtifactType
from src.generation import GenerationJobStatus
from src.generation.service import GenerationRequest, GenerationService


@dataclass
class FakeProvider:
    metadata: ProviderMetadata
    output: bytes | Artifact
    success: bool = True
    error: str | None = None

    def supports(self, capability: Capability) -> bool:
        return capability in self.metadata.capabilities

    def generate(self, request: ProviderRequest) -> ProviderResult:
        return ProviderResult(
            success=self.success,
            output=self.output if self.success else None,
            error=self.error,
        )


class MemoryStorage:
    def __init__(self) -> None:
        self.items: dict[str, bytes] = {}

    def put(self, artifact: Artifact, data: bytes) -> Artifact:
        self.items[artifact.id] = data
        return artifact

    def get(self, artifact: Artifact) -> bytes:
        return self.items[artifact.id]

    def delete(self, artifact: Artifact) -> None:
        self.items.pop(artifact.id, None)


def build_service(provider: FakeProvider, storage: ArtifactStorage) -> GenerationService:
    registry = ProviderRegistry()
    registry.register(provider)
    return GenerationService(ProviderGateway(registry), storage)


def test_generate_persists_bytes_and_completes_job() -> None:
    provider = FakeProvider(
        ProviderMetadata("fake", "Fake", frozenset({Capability.IMAGE_GENERATE})),
        b"image-bytes",
    )
    storage = MemoryStorage()
    service = build_service(provider, storage)

    result = service.generate(
        GenerationRequest(
            project_id="project-1",
            stage="image_generation",
            capability=Capability.IMAGE_GENERATE,
            payload={"prompt": "a film frame"},
            artifact_type=ArtifactType.IMAGE,
            mime_type="image/png",
        )
    )

    assert result.job.status is GenerationJobStatus.SUCCEEDED
    assert result.job.provider == "fake"
    assert len(result.artifacts) == 1
    assert result.job.output_refs == [result.artifacts[0].id]
    assert storage.items[result.artifacts[0].id] == b"image-bytes"


def test_failed_provider_marks_job_failed_without_artifacts() -> None:
    provider = FakeProvider(
        ProviderMetadata("fake", "Fake", frozenset({Capability.TEXT_GENERATE})),
        b"unused",
        success=False,
        error="provider unavailable",
    )
    service = build_service(provider, MemoryStorage())

    result = service.generate(
        GenerationRequest(
            project_id="project-1",
            stage="text_generation",
            capability=Capability.TEXT_GENERATE,
            payload={"prompt": "story"},
        )
    )

    assert result.job.status is GenerationJobStatus.FAILED
    assert result.job.error == "provider unavailable"
    assert result.artifacts == []


def test_existing_artifact_output_is_not_rewritten() -> None:
    artifact = Artifact(
        id="artifact-1",
        type=ArtifactType.VIDEO,
        uri="artifact://artifact-1",
    )
    provider = FakeProvider(
        ProviderMetadata("fake", "Fake", frozenset({Capability.VIDEO_GENERATE})),
        artifact,
    )
    storage = MemoryStorage()
    service = build_service(provider, storage)

    result = service.generate(
        GenerationRequest(
            project_id="project-1",
            stage="video_generation",
            capability=Capability.VIDEO_GENERATE,
            payload={"prompt": "scene"},
        )
    )

    assert result.job.status is GenerationJobStatus.SUCCEEDED
    assert result.artifacts == [artifact]
    assert storage.items == {}
