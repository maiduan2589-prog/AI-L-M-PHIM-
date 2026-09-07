from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class Capability(str, Enum):
    TEXT_GENERATE = "text.generate"
    IMAGE_GENERATE = "image.generate"
    VIDEO_GENERATE = "video.generate"
    SPEECH_GENERATE = "speech.generate"
    MUSIC_GENERATE = "music.generate"
    SFX_GENERATE = "sfx.generate"
    VISION_EVALUATE = "vision.evaluate"


@dataclass(frozen=True)
class ProviderMetadata:
    provider_id: str
    display_name: str
    capabilities: frozenset[Capability]
    priority: int = 100
    enabled: bool = True
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class ProviderRequest:
    capability: Capability
    payload: dict[str, Any]
    constraints: dict[str, Any] = field(default_factory=dict)


@dataclass
class ProviderResult:
    success: bool
    output: Any = None
    error: str | None = None
    retryable: bool = True
    provider_id: str | None = None


class ProviderError(RuntimeError):
    """Base error for provider boundary failures."""


class UnsupportedCapabilityError(ProviderError):
    pass
