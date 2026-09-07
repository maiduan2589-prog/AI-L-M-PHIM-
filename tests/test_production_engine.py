from production_brain.engine import ProductionEngine
from production_brain.models import ProductionContext, ProductionStage, StageResult


def test_engine_runs_to_published():
    calls = []

    def handler(stage):
        def run(_context):
            calls.append(stage.value)
            return StageResult(success=True)
        return run

    handlers = {stage: handler(stage) for stage in ProductionEngine.ORDER}
    context = ProductionContext(project_id="film-001")
    result = ProductionEngine(handlers).run(context)

    assert result.stage == ProductionStage.PUBLISHED
    assert calls == [stage.value for stage in ProductionEngine.ORDER]


def test_engine_retries_transient_failure():
    attempts = 0

    def flaky(_context):
        nonlocal attempts
        attempts += 1
        if attempts < 2:
            return StageResult(False, error="temporary", retryable=True)
        return StageResult(True)

    handlers = {stage: (flaky if stage == ProductionStage.STORY else lambda _: StageResult(True))
                for stage in ProductionEngine.ORDER}
    result = ProductionEngine(handlers, max_retries=3).run(ProductionContext(project_id="film-002"))

    assert result.stage == ProductionStage.PUBLISHED
    assert attempts == 2


def test_engine_can_resume_from_current_stage():
    calls = []

    def make(stage):
        def run(_context):
            calls.append(stage.value)
            return StageResult(True)
        return run

    handlers = {stage: make(stage) for stage in ProductionEngine.ORDER}
    context = ProductionContext(project_id="film-003", stage=ProductionStage.SCENE_BREAKDOWN)
    ProductionEngine(handlers).run(context)

    assert calls == [
        "scene_breakdown", "shot_plan", "evaluating", "revising",
        "approved", "rendered", "published",
    ]


def test_revision_loops_back_to_evaluation():
    calls = []

    def evaluate(context):
        calls.append("evaluating")
        return StageResult(True, outputs={"needs_revision": len(calls) == 1})

    handlers = {stage: (evaluate if stage == ProductionStage.EVALUATING else lambda _: StageResult(True))
                for stage in ProductionEngine.ORDER}
    result = ProductionEngine(handlers).run(ProductionContext(project_id="film-004"))

    assert result.stage == ProductionStage.PUBLISHED
    assert calls == ["evaluating", "evaluating"]
