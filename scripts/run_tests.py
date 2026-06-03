from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

PROFILE_MARKERS = {
    "fast": "not slow and not expanded and not experimental_failure",
    "expanded": "not slow and not experimental_failure",
    "slow": "not experimental_failure",
    "failing": "experimental_failure",
}


def main() -> int:
    profile = os.getenv("TEST_PROFILE", "fast")
    workers = os.getenv("PYTEST_WORKERS", "1")
    marker = PROFILE_MARKERS.get(profile)
    if marker is None:
        print(f"Unknown TEST_PROFILE={profile!r}. Expected one of: {', '.join(PROFILE_MARKERS)}")
        return 2

    Path("artifacts").mkdir(exist_ok=True)
    env = os.environ.copy()
    if profile == "failing":
        env["ENABLE_EXPERIMENTAL_FAILURE"] = "1"

    command = [
        sys.executable,
        "-m",
        "pytest",
        "-m",
        marker,
        "--junitxml=artifacts/pytest-results.xml",
    ]
    if workers != "1":
        command.extend(["-n", workers])

    return subprocess.run(command, env=env, check=False).returncode


if __name__ == "__main__":
    raise SystemExit(main())
