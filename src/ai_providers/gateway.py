from __future__ import annotations

from .models import ProviderRequest, ProviderResult
from .registry import ProviderRegistry


class ProviderGateway:
    """Vendor-neutral entry point for executing provider requests.

    The gateway resolves a provider through the registry and delegates the
    request. It deliberately does not own job lifecycle, retries, or artifact
    storage; those concerns belong to higher-level generation services.
    """

    def __init__(self, registry: ProviderRegistry) -> None:
        self._registry = registry

    def generate(
        self,
        request: ProviderRequest,
        *,
        provider_id: str | None = None,
    ) -> ProviderResult:
        provider = self._registry.select(request.capability, provider_id=provider_id)
        result = provider.generate(request)

        if result.provider_id is None:
            result.provider_id = provider.metadata.provider_id

        return result
