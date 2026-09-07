from __future__ import annotations

from .base import ProviderAdapter
from .models import Capability, ProviderMetadata


class ProviderRegistry:
    """Stores adapters and deterministically selects an enabled provider."""

    def __init__(self) -> None:
        self._providers: dict[str, ProviderAdapter] = {}

    def register(self, provider: ProviderAdapter, *, replace: bool = False) -> None:
        provider_id = provider.metadata.provider_id
        if not provider_id:
            raise ValueError("provider_id must not be empty")
        if provider_id in self._providers and not replace:
            raise ValueError(f"Provider already registered: {provider_id}")
        self._providers[provider_id] = provider

    def unregister(self, provider_id: str) -> None:
        self._providers.pop(provider_id, None)

    def get(self, provider_id: str) -> ProviderAdapter:
        try:
            return self._providers[provider_id]
        except KeyError as exc:
            raise KeyError(f"Unknown provider: {provider_id}") from exc

    def list(self) -> tuple[ProviderMetadata, ...]:
        return tuple(p.metadata for p in self._providers.values())

    def find(self, capability: Capability) -> tuple[ProviderAdapter, ...]:
        return tuple(sorted((p for p in self._providers.values() if p.metadata.enabled and p.supports(capability)), key=lambda p: (p.metadata.priority, p.metadata.provider_id)))

    def select(self, capability: Capability, provider_id: str | None = None) -> ProviderAdapter:
        if provider_id is not None:
            provider = self.get(provider_id)
            if not provider.metadata.enabled:
                raise ValueError(f"Provider is disabled: {provider_id}")
            if not provider.supports(capability):
                raise ValueError(f"Provider '{provider_id}' does not support {capability.value}")
            return provider

        candidates = self.find(capability)
        if not candidates:
            raise LookupError(f"No enabled provider supports {capability.value}")
        return candidates[0]
