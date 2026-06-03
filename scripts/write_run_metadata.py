from __future__ import annotations

import argparse
import json
import os
from datetime import UTC, datetime
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser(description="Write workflow input metadata as JSON.")
    parser.add_argument("--output", default="artifacts/run-metadata.json")
    args = parser.parse_args()

    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)

    metadata = {
        "cache_mode": os.getenv("CACHE_MODE", "enabled"),
        "execution_mode": os.getenv("EXECUTION_MODE", "parallel"),
        "test_profile": os.getenv("TEST_PROFILE", "fast"),
        "pytest_workers": os.getenv("PYTEST_WORKERS", "1"),
        "github_run_id": os.getenv("GITHUB_RUN_ID"),
        "github_run_attempt": os.getenv("GITHUB_RUN_ATTEMPT"),
        "github_sha": os.getenv("GITHUB_SHA"),
        "github_ref_name": os.getenv("GITHUB_REF_NAME"),
        "generated_at": datetime.now(UTC).isoformat(),
    }
    output.write_text(json.dumps(metadata, indent=2, sort_keys=True), encoding="utf-8")
    print(f"Wrote {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
