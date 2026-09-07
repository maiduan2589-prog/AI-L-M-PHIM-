from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class ProjectBrief:
    """Normalized creative input accepted by the planning layer."""

    title: str
    idea: str
    language: str = "vi"
    genre: str = ""
    target_duration_seconds: int = 300
    tone: str = ""
    audience: str = ""
    constraints: list[str] = field(default_factory=list)


@dataclass
class StoryPlan:
    logline: str
    premise: str
    synopsis: str
    structure: dict[str, Any]
    themes: list[str] = field(default_factory=list)
    constraints: list[str] = field(default_factory=list)
    version: int = 1


@dataclass
class ScreenplayPlan:
    scenes: list[dict[str, Any]]
    version: int = 1


@dataclass
class ShotPlan:
    shots: list[dict[str, Any]]
    version: int = 1


def validate_brief(brief: ProjectBrief) -> None:
    if not brief.title.strip():
        raise ValueError("title is required")
    if not brief.idea.strip():
        raise ValueError("idea is required")
    if brief.target_duration_seconds <= 0:
        raise ValueError("target_duration_seconds must be > 0")


def build_story_input(brief: ProjectBrief) -> dict[str, Any]:
    validate_brief(brief)
    return {
        "title": brief.title.strip(),
        "idea": brief.idea.strip(),
        "language": brief.language,
        "genre": brief.genre,
        "target_duration_seconds": brief.target_duration_seconds,
        "tone": brief.tone,
        "audience": brief.audience,
        "constraints": list(brief.constraints),
    }
