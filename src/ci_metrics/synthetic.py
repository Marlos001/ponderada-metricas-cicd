from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
from math import sqrt
from time import perf_counter


@dataclass(frozen=True)
class TestBatchSummary:
    case_count: int
    elapsed_seconds: float
    checksum: float

    @property
    def average_case_seconds(self) -> float:
        if self.case_count == 0:
            return 0.0
        return self.elapsed_seconds / self.case_count


def normalize_duration(seconds: float) -> float:
    if seconds < 0:
        raise ValueError("duration cannot be negative")
    return round(seconds, 3)


def classify_pipeline_duration(seconds: float) -> str:
    if seconds < 60:
        return "fast"
    if seconds < 180:
        return "moderate"
    return "slow"


def estimate_feedback_score(duration_seconds: float, failure_rate_value: float) -> float:
    if not 0 <= failure_rate_value <= 1:
        raise ValueError("failure rate must be between 0 and 1")
    duration_penalty = min(duration_seconds / 300, 1)
    reliability_penalty = failure_rate_value
    return round(100 * (1 - (0.7 * duration_penalty + 0.3 * reliability_penalty)), 2)


def summarize_numeric_cases(values: Iterable[int]) -> TestBatchSummary:
    started = perf_counter()
    checksum = 0.0
    case_count = 0
    for value in values:
        checksum += sqrt(value * value + 3)
        case_count += 1
    elapsed = perf_counter() - started
    return TestBatchSummary(
        case_count=case_count,
        elapsed_seconds=elapsed,
        checksum=round(checksum, 6),
    )
