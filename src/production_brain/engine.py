from __future__ import annotations

from collections.abc import Callable

from .models import ProductionContext, ProductionStage, StageResult

StageHandler = Callable[[ProductionContext], StageResult]


class ProductionEngine:
    """Provider-agnostic, resumable production state machine."""

    ORDER = (
        ProductionStage.PLANNED,
        ProductionStage.STORY,
        ProductionStage.SCREENPLAY,
        ProductionStage.SCENE_BREAKDOWN,
        ProductionStage.SHOT_PLAN,
        ProductionStage.EVALUATING,
        ProductionStage.REVISING,
        ProductionStage.APPROVED,
        ProductionStage.RENDERED,
        ProductionStage.PUBLISHED,
    )

    def __init__(self, handlers: dict[ProductionStage, StageHandler], max_retries: int = 3) -> None:
        if max_retries < 1:
            raise ValueError("max_retries must be >= 1")
        self.handlers = handlers
        self.max_retries = max_retries

    def run(self, context: ProductionContext) -> ProductionContext:
        if context.stage in (ProductionStage.PUBLISHED, ProductionStage.FAILED):
            if context.stage == ProductionStage.FAILED:
                raise RuntimeError("Cannot resume a failed context without resetting its stage")
            return context

        for stage in self.ORDER[self.ORDER.index(context.stage):]:
            handler = self.handlers.get(stage)
            if handler is None:
                raise KeyError(f"No handler registered for stage: {stage.value}")

            result = self._execute_with_retry(stage, handler, context)
            if not result.success:
                context.stage = ProductionStage.FAILED
                context.record("production_failed", stage=stage.value, error=result.error)
                raise RuntimeError(result.error or f"Stage failed: {stage.value}")

            context.data.update(result.outputs)
            context.record("stage_completed", stage=stage.value, outputs=result.outputs)

            if stage == ProductionStage.EVALUATING and context.data.get("needs_revision"):
                context.stage = ProductionStage.REVISING
                continue
            if stage == ProductionStage.REVISING:
                context.data["needs_revision"] = False
                context.stage = ProductionStage.EVALUATING
                continue
            context.stage = stage

        return context

    def _execute_with_retry(self, stage: ProductionStage, handler: StageHandler, context: ProductionContext) -> StageResult:
        for _ in range(self.max_retries):
            attempt = context.increment_attempt(stage)
            context.record("stage_started", stage=stage.value, attempt=attempt)
            try:
                result = handler(context)
            except Exception as exc:  # noqa: BLE001
                result = StageResult(False, error=str(exc), retryable=True)
            if result.success:
                return result
            context.record("stage_error", stage=stage.value, attempt=attempt, error=result.error)
            if not result.retryable:
                return result
        return StageResult(False, error=f"Stage {stage.value} exceeded retry limit ({self.max_retries})", retryable=False)
