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
from src.generation import GenerationJob, GenerationJobStatus
from src.generation.service import GenerationRequest, GenerationService


@dataclass
class FakeProvider:
    metadata: ProviderMetadata
    output: bytes | Artifact | str
    success: bool = True
    error: str | None = None
    raises: Exception | None = None

    def supports(self, capability: Capability) -> bool:
        return capability in self.metadata.capabilities

    def generate(self, request: ProviderRequest) -> ProviderResult:
        if self.raises is not None:
            raise self.raises
        return ProviderResult(
            success=self.success,
            output=self.output if self.success else None,
            error=self.error,
        )


class MemoryStorage:
    def __init__(self) -> None:
        self.items: dict[str, bytes] = {}
        self.raises: Exception | None = None

    def put(self, artifact: Artifact, data: bytes) -> Artifact:
        if self.raises is not None:
            raise self.raises
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


def test_provider_exception_marks_job_failed() -> None:
    provider = FakeProvider(
        ProviderMetadata("fake", "Fake", frozenset({Capability.VIDEO_GENERATE})),
        b"unused",
        raises=RuntimeError("provider crashed"),
    )
    service = build_service(provider, MemoryStorage())

    result = service.generate(
        GenerationRequest(
            project_id="project-1",
            stage="video_generation",
            capability=Capability.VIDEO_GENERATE,
            payload={"prompt": "scene"},
        )
    )

    assert result.job.status is GenerationJobStatus.FAILED
    assert result.job.error == "provider crashed"
    assert result.artifacts == []


def test_storage_exception_marks_job_failed_without_partial_success() -> None:
    provider = FakeProvider(
        ProviderMetadata("fake", "Fake", frozenset({Capability.IMAGE_GENERATE})),
        b"image-bytes",
    )
    storage = MemoryStorage()
    storage.raises = OSError("storage unavailable")
    service = build_service(provider, storage)

    result = service.generate(
        GenerationRequest(
            project_id="project-1",
            stage="image_generation",
            capability=Capability.IMAGE_GENERATE,
            payload={"prompt": "a film frame"},
            artifact_type=ArtifactType.IMAGE,
        )
    )

    assert result.job.status is GenerationJobStatus.FAILED
    assert result.job.error == "storage unavailable"
    assert result.artifacts == []
    assert result.job.output_refs == []
    assert storage.items == {}


def test_invalid_provider_output_marks_job_failed() -> None:
    provider = FakeProvider(
        ProviderMetadata("fake", "Fake", frozenset({Capability.TEXT_GENERATE})),
        "not-bytes",
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
    assert result.job.error == "Provider output must be bytes or Artifact"
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


def test_failed_job_can_be_marked_running_again_for_retry() -> None:
    job = GenerationJob(
        id="job-1",
        project_id="project-1",
        stage="image_generation",
        provider="fake",
        capability=Capability.IMAGE_GENERATE,
    )

    job.mark_running()
    job.mark_failed("temporary failure")
    job.mark_running()

    assert job.status is GenerationJobStatus.RUNNING
    assert job.attempt == 2
    assert job.error is None
