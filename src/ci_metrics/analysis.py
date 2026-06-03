from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from statistics import mean


@dataclass(frozen=True)
class JobMeasurement:
    name: str
    started_at: datetime
    completed_at: datetime
    conclusion: str

    @property
    def duration_seconds(self) -> float:
        return duration_seconds(self.started_at, self.completed_at)


@dataclass(frozen=True)
class RunMeasurement:
    run_id: int
    commit_sha: str
    commit_message: str
    status: str
    started_at: datetime
    completed_at: datetime
    jobs: tuple[JobMeasurement, ...]

    @property
    def workflow_duration_seconds(self) -> float:
        return duration_seconds(self.started_at, self.completed_at)

    @property
    def failed_jobs(self) -> tuple[JobMeasurement, ...]:
        return tuple(job for job in self.jobs if job.conclusion not in {"success", "skipped"})


def duration_seconds(started_at: datetime, completed_at: datetime) -> float:
    start = _as_utc(started_at)
    end = _as_utc(completed_at)
    if end < start:
        raise ValueError("completed_at must be greater than or equal to started_at")
    return (end - start).total_seconds()


def average(values: list[float] | tuple[float, ...]) -> float:
    if not values:
        return 0.0
    return float(mean(values))


def success_rate(statuses: list[str] | tuple[str, ...]) -> float:
    if not statuses:
        return 0.0
    successes = sum(1 for status in statuses if status == "success")
    return successes / len(statuses)


def failure_rate(statuses: list[str] | tuple[str, ...]) -> float:
    if not statuses:
        return 0.0
    failures = sum(1 for status in statuses if status in {"failure", "cancelled", "timed_out"})
    return failures / len(statuses)


def _as_utc(value: datetime) -> datetime:
    if value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc)
