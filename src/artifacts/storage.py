from __future__ import annotations

from typing import Protocol

from .models import Artifact


class ArtifactStorage(Protocol):
    """Storage boundary for artifact bytes and their stable references."""

    def put(self, artifact: Artifact, data: bytes) -> Artifact:
        """Persist artifact data and return its canonical metadata."""
        ...

    def get(self, artifact: Artifact) -> bytes:
        """Read artifact data by its stable reference."""
        ...

    def delete(self, artifact: Artifact) -> None:
        """Delete artifact data."""
        ...
