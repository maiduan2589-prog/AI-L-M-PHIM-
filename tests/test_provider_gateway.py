from dataclasses import dataclass

from src.ai_providers import Capability, ProviderMetadata, ProviderRegistry, ProviderRequest, ProviderResult
from src.ai_providers.gateway import ProviderGateway


@dataclass
class FakeProvider:
    metadata: ProviderMetadata

    def supports(self, capability: Capability) -> bool:
        return capability in self.metadata.capabilities

    def generate(self, request: ProviderRequest) -> ProviderResult:
        return ProviderResult(success=True, output=request.payload, provider_id=self.metadata.provider_id)


def provider(provider_id: str, *capabilities: Capability, priority: int = 100) -> FakeProvider:
    return FakeProvider(ProviderMetadata(provider_id, provider_id, frozenset(capabilities), priority))


def test_gateway_selects_provider_and_delegates_request():
    registry = ProviderRegistry()
    preferred = provider("preferred", Capability.TEXT_GENERATE, priority=10)
    fallback = provider("fallback", Capability.TEXT_GENERATE, priority=20)
    registry.register(fallback)
    registry.register(preferred)

    request = ProviderRequest(Capability.TEXT_GENERATE, {"prompt": "hello"})
    result = ProviderGateway(registry).generate(request)

    assert result.success is True
    assert result.output == {"prompt": "hello"}
    assert result.provider_id == "preferred"


def test_gateway_allows_explicit_provider_selection():
    registry = ProviderRegistry()
    first = provider("first", Capability.IMAGE_GENERATE, priority=10)
    second = provider("second", Capability.IMAGE_GENERATE, priority=20)
    registry.register(first)
    registry.register(second)

    request = ProviderRequest(Capability.IMAGE_GENERATE, {"prompt": "scene"})
    result = ProviderGateway(registry).generate(request, provider_id="second")

    assert result.provider_id == "second"


def test_gateway_preserves_provider_result_without_adding_job_lifecycle():
    class ResultProvider(FakeProvider):
        def generate(self, request: ProviderRequest) -> ProviderResult:
            return ProviderResult(success=False, error="temporary", retryable=True)

    registry = ProviderRegistry()
    registry.register(ResultProvider(ProviderMetadata("p", "p", frozenset({Capability.VIDEO_GENERATE}))))

    result = ProviderGateway(registry).generate(
        ProviderRequest(Capability.VIDEO_GENERATE, {"prompt": "shot"})
    )

    assert result.success is False
    assert result.error == "temporary"
    assert result.retryable is True
    assert result.provider_id == "p"
