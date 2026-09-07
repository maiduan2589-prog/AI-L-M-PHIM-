from datetime import datetime, timezone

import pytest

from src.ai_providers import Capability
from src.generation import GenerationJob, GenerationJobStatus


def make_job() -> GenerationJob:
    return GenerationJob(
        id="job-1",
        project_id="project-1",
        stage="shot_generation",
        provider="fake",
        capability=Capability.IMAGE_GENERATE,
        input_refs=["prompt-1"],
    )


def test_job_starts_queued_and_tracks_attempts():
    job = make_job()
    assert job.status is GenerationJobStatus.QUEUED
    assert job.attempt == 0
    assert job.completed_at is None

    job.mark_running()
    assert job.status is GenerationJobStatus.RUNNING
    assert job.attempt == 1
    assert job.error is None


def test_job_success_records_outputs_and_completion_time():
    job = make_job()
    job.mark_running()
    job.mark_succeeded(["image-1"])

    assert job.status is GenerationJobStatus.SUCCEEDED
    assert job.output_refs == ["image-1"]
    assert job.completed_at is not None
    assert job.completed_at.tzinfo is not None


def test_failed_job_can_be_retried_as_a_new_attempt():
    job = make_job()
    job.mark_running()
    job.mark_failed("provider timeout")

    assert job.status is GenerationJobStatus.FAILED
    assert job.error == "provider timeout"
    first_completed_at = job.completed_at

    job.mark_running()
    assert job.status is GenerationJobStatus.RUNNING
    assert job.attempt == 2
    assert job.completed_at is None
    assert first_completed_at is not None


def test_cancelled_job_cannot_be_restarted():
    job = make_job()
    job.cancel()

    assert job.status is GenerationJobStatus.CANCELLED
    assert job.completed_at is not None
    with pytest.raises(ValueError, match="Cannot run job"):
        job.mark_running()


def test_completed_job_cannot_change_lifecycle():
    job = make_job()
    job.mark_running()
    job.mark_succeeded()

    with pytest.raises(ValueError, match="Cannot fail job"):
        job.mark_failed("late error")
    with pytest.raises(ValueError, match="Cannot cancel job"):
        job.cancel()


def test_timestamps_are_utc():
    job = make_job()
    assert job.created_at.tzinfo == timezone.utc
