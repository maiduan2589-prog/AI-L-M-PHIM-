from __future__ import annotations

from collections.abc import Callable
from typing import Any

from .models import ProductionContext, ProductionStage, StageResult

StageHandler = Callable[[ProductionContext], StageResult]


class ProductionEngine:
    """Small, resumable state machine for autonomous film production.

    Handlers are injected so the engine stays provider-agnostic. A handler may
    call an LLM, image model, video model, renderer, or another service without
    coupling the orchestration layer to a vendor.
    """

    ORDER = (
        ProductionStage.PLANNED,
        ProductionStage.RUNNING,
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
        """Run from the context's current stage and stop only on success/failure.

        Persisting ``context`` outside this class makes the workflow resumable:
        after a process crash, reload the context and call ``run`` again.
        """
        if context.stage == ProductionStage.PUBLISHED:
            return context
        if context.stage == ProductionStage.FAILED:
            raise RuntimeError("Cannot resume a failed context without resetting its stage")

        start_index = self.ORDER.index(context.stage)
        for stage in self.ORDER[start_index:]:
            if stage == ProductionStage.PUBLISHED:
                context.stage = stage
                context.record("stage_completed", stage=stage.value)
                return context

            handler = self.handlers.get(stage)
            if handler is None:
                raise KeyError(f"No handler registered for stage: {stage.value}")

            context.stage = ProductionStage.RUNNING
            result = self._execute_with_retry(stage, handler, context)
            if not result.success:
                context.stage = ProductionStage.FAILED
                context.record("production_failed", stage=stage.value, error=result.error)
                raise RuntimeError(result.error or f"Stage failed: {stage.value}")

            context.data.update(result.outputs)
            context.record("stage_completed", stage=stage.value, outputs=result.outputs)
            context.stage = stage

            # Evaluation and revision are deliberately explicit stages. A
            # future evaluator can set data["needs_revision"] to drive a loop.
            if stage == ProductionStage.EVALUATING and context.data.get("needs_revision"):
                context.stage = ProductionStage.REVISING

        return context

    def _execute_with_retry(
        self, stage: ProductionStage, handler: StageHandler, context: ProductionContext
    ) -> StageResult:
        for _ in range(self.max_retries):
            attempt = context.increment_attempt(stage)
            context.record("stage_started", stage=stage.value, attempt=attempt)
            try:
                result = handler(context)
            except Exception as exc:  # noqa: BLE001 - orchestration boundary
                result = StageResult(success=False, error=str(exc), retryable=True)

            if result.success:
                return result
            context.record("stage_error", stage=stage.value, attempt=attempt, error=result.error)
            if not result.retryable:
                return result

        return StageResult(
            success=False,
            error=f"Stage {stage.value} exceeded retry limit ({self.max_retries})",
            retryable=False,
        )
