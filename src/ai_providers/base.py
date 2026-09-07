from __future__ import annotations

from typing import Protocol

from .models import Capability, ProviderMetadata, ProviderRequest, ProviderResult


class ProviderAdapter(Protocol):
    """Vendor-neutral contract implemented by every AI provider adapter."""

    @property
    def metadata(self) -> ProviderMetadata:
        ...

    def generate(self, request: ProviderRequest) -> ProviderResult:
        """Execute a supported capability and return a normalized result."""
        ...

    def supports(self, capability: Capability) -> bool:
        return capability in self.metadata.capabilities
