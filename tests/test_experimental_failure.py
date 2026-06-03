from __future__ import annotations

import os

import pytest


@pytest.mark.experimental_failure
def test_controlled_failure_variant() -> None:
    if os.getenv("ENABLE_EXPERIMENTAL_FAILURE") != "1":
        pytest.skip("controlled failure is disabled")

    assert False, "controlled failure for CI stability measurement"
