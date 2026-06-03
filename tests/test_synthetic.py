from __future__ import annotations

from time import sleep

import pytest

from ci_metrics.synthetic import (
    classify_pipeline_duration,
    estimate_feedback_score,
    normalize_duration,
    summarize_numeric_cases,
)


@pytest.mark.parametrize(
    ("seconds", "expected"),
    [
        (0, 0),
        (1.23456, 1.235),
        (59.999, 59.999),
    ],
)
def test_normalize_duration(seconds: float, expected: float) -> None:
    assert normalize_duration(seconds) == expected


def test_normalize_duration_rejects_negative_values() -> None:
    with pytest.raises(ValueError, match="negative"):
        normalize_duration(-0.1)


@pytest.mark.parametrize(
    ("seconds", "expected"),
    [
        (20, "fast"),
        (120, "moderate"),
        (240, "slow"),
    ],
)
def test_classify_pipeline_duration(seconds: float, expected: str) -> None:
    assert classify_pipeline_duration(seconds) == expected


def test_estimate_feedback_score_penalizes_duration_and_failure() -> None:
    assert estimate_feedback_score(30, 0) > estimate_feedback_score(240, 0.25)


def test_estimate_feedback_score_rejects_invalid_failure_rate() -> None:
    with pytest.raises(ValueError, match="between 0 and 1"):
        estimate_feedback_score(10, 1.2)


@pytest.mark.expanded
@pytest.mark.parametrize("case_size", list(range(20, 220)))
def test_summarize_numeric_cases_expanded(case_size: int) -> None:
    summary = summarize_numeric_cases(range(case_size))

    assert summary.case_count == case_size
    assert summary.checksum >= 0


@pytest.mark.slow
@pytest.mark.parametrize("case_size", [5000, 7500, 10000])
def test_summarize_numeric_cases_slow(case_size: int) -> None:
    sleep(0.75)
    summary = summarize_numeric_cases(range(case_size))

    assert summary.average_case_seconds >= 0
