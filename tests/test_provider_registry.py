from dataclasses import dataclass

import pytest

from src.ai_providers import Capability, ProviderMetadata, ProviderRegistry, ProviderRequest, ProviderResult


@dataclass
class FakeProvider:
    metadata: ProviderMetadata

    def supports(self, capability: Capability) -> bool:
        return capability in self.metadata.capabilities

    def generate(self, request: ProviderRequest) -> ProviderResult:
        return ProviderResult(success=True, output=request.payload, provider_id=self.metadata.provider_id)


def provider(provider_id: str, *capabilities: Capability, priority: int = 100, enabled: bool = True) -> FakeProvider:
    return FakeProvider(ProviderMetadata(provider_id, provider_id, frozenset(capabilities), priority, enabled))


def test_register_and_select_lowest_priority():
    registry = ProviderRegistry()
    slow = provider("slow", Capability.TEXT_GENERATE, priority=50)
    fast = provider("fast", Capability.TEXT_GENERATE, priority=10)
    registry.register(slow)
    registry.register(fast)
    assert registry.select(Capability.TEXT_GENERATE) is fast


def test_duplicate_provider_requires_replace():
    registry = ProviderRegistry()
    registry.register(provider("p", Capability.IMAGE_GENERATE))
    with pytest.raises(ValueError, match="already registered"):
        registry.register(provider("p", Capability.IMAGE_GENERATE))


def test_disabled_provider_is_not_selected():
    registry = ProviderRegistry()
    registry.register(provider("disabled", Capability.VIDEO_GENERATE, enabled=False))
    with pytest.raises(LookupError, match="No enabled provider"):
        registry.select(Capability.VIDEO_GENERATE)


def test_explicit_provider_must_support_capability():
    registry = ProviderRegistry()
    registry.register(provider("text", Capability.TEXT_GENERATE))
    with pytest.raises(ValueError, match="does not support"):
        registry.select(Capability.IMAGE_GENERATE, provider_id="text")


def test_unregister_removes_provider():
    registry = ProviderRegistry()
    registry.register(provider("p", Capability.SFX_GENERATE))
    registry.unregister("p")
    with pytest.raises(KeyError, match="Unknown provider"):
        registry.get("p")
