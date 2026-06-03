from __future__ import annotations

from datetime import UTC, datetime

import pytest

from ci_metrics.analysis import (
    JobMeasurement,
    RunMeasurement,
    average,
    duration_seconds,
    failure_rate,
    success_rate,
)


def test_duration_seconds_accepts_timezone_aware_datetimes() -> None:
    start = datetime(2026, 6, 3, 10, 0, tzinfo=UTC)
    end = datetime(2026, 6, 3, 10, 2, 30, tzinfo=UTC)

    assert duration_seconds(start, end) == 150


def test_duration_seconds_rejects_negative_interval() -> None:
    start = datetime(2026, 6, 3, 10, 2, tzinfo=UTC)
    end = datetime(2026, 6, 3, 10, 0, tzinfo=UTC)

    with pytest.raises(ValueError, match="completed_at"):
        duration_seconds(start, end)


@pytest.mark.parametrize(
    ("values", "expected"),
    [
        ([1.0, 2.0, 3.0], 2.0),
        ([], 0.0),
        ((4.0, 6.0), 5.0),
    ],
)
def test_average(values: list[float] | tuple[float, ...], expected: float) -> None:
    assert average(values) == expected


def test_success_and_failure_rates() -> None:
    statuses = ("success", "failure", "success", "cancelled")

    assert success_rate(statuses) == 0.5
    assert failure_rate(statuses) == 0.5


def test_run_measurement_reports_failed_jobs() -> None:
    start = datetime(2026, 6, 3, 10, 0, tzinfo=UTC)
    end = datetime(2026, 6, 3, 10, 1, tzinfo=UTC)
    jobs = (
        JobMeasurement("lint", start, end, "success"),
        JobMeasurement("tests", start, end, "failure"),
    )

    run = RunMeasurement(1, "abc123", "experiment", "failure", start, end, jobs)

    assert run.workflow_duration_seconds == 60
    assert [job.name for job in run.failed_jobs] == ["tests"]
