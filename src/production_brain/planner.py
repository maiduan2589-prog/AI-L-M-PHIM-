from __future__ import annotations

from collections.abc import Callable
from typing import Any

from .models import ProductionContext, ProductionStage, StageResult
from .planning import ProjectBrief, build_story_input

Planner = Callable[[dict[str, Any]], dict[str, Any]]


class ProductionPlanner:
    """Transforms a normalized brief into structured production artifacts.

    AI calls are injected as functions. This keeps prompts/models/providers out
    of the domain and makes each planning stage independently testable.
    """

    def __init__(
        self,
        story: Planner,
        screenplay: Planner,
        scene_breakdown: Planner,
        shot_plan: Planner,
    ) -> None:
        self.story = story
        self.screenplay = screenplay
        self.scene_breakdown = scene_breakdown
        self.shot_plan = shot_plan

    def plan_story(self, context: ProductionContext) -> StageResult:
        brief = self._brief(context)
        return self._call(self.story, build_story_input(brief), "story")

    def plan_screenplay(self, context: ProductionContext) -> StageResult:
        story = context.data.get("story")
        if not story:
            return StageResult(False, error="story output is required", retryable=False)
        return self._call(self.screenplay, {"story": story}, "screenplay")

    def plan_scenes(self, context: ProductionContext) -> StageResult:
        screenplay = context.data.get("screenplay")
        if not screenplay:
            return StageResult(False, error="screenplay output is required", retryable=False)
        return self._call(self.scene_breakdown, {"screenplay": screenplay}, "scenes")

    def plan_shots(self, context: ProductionContext) -> StageResult:
        scenes = context.data.get("scenes")
        if not scenes:
            return StageResult(False, error="scene breakdown output is required", retryable=False)
        return self._call(self.shot_plan, {"scenes": scenes}, "shot_plan")

    @staticmethod
    def _brief(context: ProductionContext) -> ProjectBrief:
        value = context.data.get("brief")
        if isinstance(value, ProjectBrief):
            return value
        if not isinstance(value, dict):
            raise ValueError("context.data['brief'] must contain a ProjectBrief or dictionary")
        return ProjectBrief(**value)

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
    """Create engine handlers for the planning sequence."""
    return {
        ProductionStage.PLANNED: planner.plan_story,
        ProductionStage.EVALUATING: planner.plan_screenplay,
        ProductionStage.REVISING: planner.plan_scenes,
        ProductionStage.APPROVED: planner.plan_shots,
    }
