from __future__ import annotations

from collections.abc import Callable
from typing import Any

from .models import ProductionContext, ProductionStage, StageResult
from .planning import ProjectBrief, build_story_input

Planner = Callable[[dict[str, Any]], dict[str, Any]]


class ProductionPlanner:
    """Transforms a normalized brief into structured production artifacts."""

    def __init__(self, story: Planner, screenplay: Planner, scene_breakdown: Planner, shot_plan: Planner) -> None:
        self.story = story
        self.screenplay = screenplay
        self.scene_breakdown = scene_breakdown
        self.shot_plan = shot_plan

    def plan_story(self, context: ProductionContext) -> StageResult:
        return self._call(self.story, build_story_input(self._brief(context)), "story")

    def plan_screenplay(self, context: ProductionContext) -> StageResult:
        return self._required(self.screenplay, context, "story", "screenplay")

    def plan_scenes(self, context: ProductionContext) -> StageResult:
        return self._required(self.scene_breakdown, context, "screenplay", "scenes")

    def plan_shots(self, context: ProductionContext) -> StageResult:
        return self._required(self.shot_plan, context, "scenes", "shot_plan")

    @staticmethod
    def _brief(context: ProductionContext) -> ProjectBrief:
        value = context.data.get("brief")
        if isinstance(value, ProjectBrief):
            return value
        if not isinstance(value, dict):
            raise ValueError("context.data['brief'] must contain a ProjectBrief or dictionary")
        return ProjectBrief(**value)

    @staticmethod
    def _required(planner: Planner, context: ProductionContext, input_key: str, output_key: str) -> StageResult:
        value = context.data.get(input_key)
        if not value:
            return StageResult(False, error=f"{input_key} output is required", retryable=False)
        return ProductionPlanner._call(planner, {input_key: value}, output_key)

    @staticmethod
    def _call(planner: Planner, payload: dict[str, Any], key: str) -> StageResult:
        try:
            output = planner(payload)
        except Exception as exc:  # noqa: BLE001 - adapter boundary
            return StageResult(False, error=str(exc), retryable=True)
        if not isinstance(output, dict):
            return StageResult(False, error=f"{key} planner must return a dictionary", retryable=False)
        return StageResult(True, outputs={key: output})


def build_planning_handlers(planner: ProductionPlanner) -> dict[ProductionStage, Callable[[ProductionContext], StageResult]]:
    """Register only the four planning stages; execution/QA stages are separate."""
    return {
        ProductionStage.STORY: planner.plan_story,
        ProductionStage.SCREENPLAY: planner.plan_screenplay,
        ProductionStage.SCENE_BREAKDOWN: planner.plan_scenes,
        ProductionStage.SHOT_PLAN: planner.plan_shots,
    }
