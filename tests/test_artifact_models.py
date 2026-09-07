from src.artifacts import Artifact, ArtifactType


def test_artifact_records_stable_reference_and_metadata():
    artifact = Artifact(
        id="artifact-1",
        type=ArtifactType.VIDEO,
        uri="storage://films/project-1/shot-1.mp4",
        mime_type="video/mp4",
        size_bytes=1024,
        checksum="sha256:abc",
    )

    assert artifact.id == "artifact-1"
    assert artifact.type is ArtifactType.VIDEO
    assert artifact.uri.startswith("storage://")
    assert artifact.size_bytes == 1024


def test_artifact_rejects_invalid_reference():
    try:
        Artifact(id="artifact-1", type=ArtifactType.IMAGE, uri="")
    except ValueError as exc:
        assert "uri" in str(exc)
    else:
        raise AssertionError("Expected invalid URI to be rejected")


def test_artifact_rejects_negative_size():
    try:
        Artifact(
            id="artifact-1",
            type=ArtifactType.IMAGE,
            uri="storage://image.png",
            size_bytes=-1,
        )
    except ValueError as exc:
        assert "size_bytes" in str(exc)
    else:
        raise AssertionError("Expected negative size to be rejected")
