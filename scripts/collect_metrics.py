from __future__ import annotations

import argparse
import csv
import io
import json
import os
import tempfile
import zipfile
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import requests
from junitparser import JUnitXml

API_ROOT = "https://api.github.com"


@dataclass(frozen=True)
class TestMetrics:
    test_count: int | None
    test_failures: int | None
    test_errors: int | None
    test_skipped: int | None
    test_time_seconds: float | None

    @property
    def average_test_seconds(self) -> float | None:
        test_count = self.test_count
        if test_count is None or test_count == 0 or self.test_time_seconds is None:
            return None
        return self.test_time_seconds / test_count


def main() -> int:
    parser = argparse.ArgumentParser(description="Collect GitHub Actions CI/CD metrics.")
    parser.add_argument("--owner", required=True)
    parser.add_argument("--repo", required=True)
    parser.add_argument("--workflow", default="ci.yml")
    parser.add_argument("--limit", type=int, default=30)
    parser.add_argument("--output", default="data/pipeline_metrics.csv")
    parser.add_argument("--raw-output", default="data/raw_runs.json")
    parser.add_argument("--manifest-output", default="data/run_manifest.csv")
    parser.add_argument("--steps-output", default="data/step_metrics.csv")
    parser.add_argument("--artifacts-dir", default=None)
    parser.add_argument(
        "--local-artifacts-only",
        action="store_true",
        help="Parse downloaded artifact directories without calling the GitHub API.",
    )
    args = parser.parse_args()

    token = os.getenv("GITHUB_TOKEN")
    if args.local_artifacts_only:
        if args.artifacts_dir is None:
            raise SystemExit("--artifacts-dir is required with --local-artifacts-only.")
        local_rows = collect_local_artifacts(Path(args.artifacts_dir))
        write_csv(Path(args.output), local_rows)
        write_json(Path(args.raw_output), local_rows)
        print(f"Wrote local artifact metrics to {args.output} and {args.raw_output}")
        return 0

    if not token:
        raise SystemExit("GITHUB_TOKEN is required to collect metrics from GitHub API.")

    session = requests.Session()
    session.headers.update(
        {
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {token}",
            "X-GitHub-Api-Version": "2022-11-28",
        }
    )

    repo_full_name = f"{args.owner}/{args.repo}"
    runs = fetch_workflow_runs(session, repo_full_name, args.workflow, args.limit)
    normalized_runs: list[dict[str, Any]] = []
    rows: list[dict[str, Any]] = []
    step_rows: list[dict[str, Any]] = []
    manifest_rows: list[dict[str, Any]] = []

    for run in runs:
        jobs = fetch_run_jobs(session, repo_full_name, run["id"])
        test_metrics = load_test_metrics(session, repo_full_name, run["id"], args.artifacts_dir)
        run_started = parse_github_datetime(run["run_started_at"] or run["created_at"])
        run_completed = parse_github_datetime(run["updated_at"])
        workflow_duration = duration_seconds(run_started, run_completed)
        commit_message = (run.get("head_commit") or {}).get("message") or ""
        commit_summary = commit_message.splitlines()[0] if commit_message else ""
        conclusion = run.get("conclusion") or run.get("status")
        variant = infer_variant(run, commit_summary)

        normalized_runs.append(
            {
                "run": run,
                "jobs": jobs,
                "test_metrics": test_metrics.__dict__,
                "variant": variant,
            }
        )
        manifest_rows.append(
            {
                "run_id": run["id"],
                "run_number": run["run_number"],
                "commit_sha": run["head_sha"],
                "commit_message": commit_summary,
                "status": conclusion,
                "timestamp": run_started.isoformat(),
                "workflow_duration": round(workflow_duration, 3),
                **variant,
            }
        )

        for job in jobs:
            job_started = parse_github_datetime(job["started_at"])
            job_completed = parse_github_datetime(job["completed_at"])
            rows.append(
                {
                    "run_id": run["id"],
                    "run_number": run["run_number"],
                    "commit_sha": run["head_sha"],
                    "commit_message": commit_summary,
                    "status": conclusion,
                    "workflow_duration": round(workflow_duration, 3),
                    "job_name": job["name"],
                    "job_status": job.get("conclusion") or job.get("status"),
                    "job_duration": round(duration_seconds(job_started, job_completed), 3),
                    "test_count": test_metrics.test_count,
                    "test_failures": test_metrics.test_failures,
                    "test_errors": test_metrics.test_errors,
                    "test_skipped": test_metrics.test_skipped,
                    "test_time_seconds": test_metrics.test_time_seconds,
                    "average_test_seconds": test_metrics.average_test_seconds,
                    "timestamp": run_started.isoformat(),
                    **variant,
                }
            )
            for step in job.get("steps", []):
                step_started = step.get("started_at")
                step_completed = step.get("completed_at")
                step_duration = None
                if step_started and step_completed:
                    step_duration = round(
                        duration_seconds(
                            parse_github_datetime(step_started),
                            parse_github_datetime(step_completed),
                        ),
                        3,
                    )
                step_rows.append(
                    {
                        "run_id": run["id"],
                        "run_number": run["run_number"],
                        "commit_sha": run["head_sha"],
                        "status": conclusion,
                        "job_name": job["name"],
                        "step_name": step.get("name"),
                        "step_status": step.get("conclusion") or step.get("status"),
                        "step_number": step.get("number"),
                        "step_duration": step_duration,
                        "timestamp": run_started.isoformat(),
                        **variant,
                    }
                )

    write_csv(Path(args.output), rows)
    write_csv(Path(args.steps_output), step_rows)
    write_csv(Path(args.manifest_output), manifest_rows)
    write_json(Path(args.raw_output), normalized_runs)
    print(
        f"Wrote {args.output}, {args.steps_output}, "
        f"{args.manifest_output}, and {args.raw_output}"
    )
    return 0


def fetch_workflow_runs(
    session: requests.Session, repo_full_name: str, workflow: str, limit: int
) -> list[dict[str, Any]]:
    url = f"{API_ROOT}/repos/{repo_full_name}/actions/workflows/{workflow}/runs"
    params: dict[str, str | int] = {
        "per_page": min(limit, 100),
        "exclude_pull_requests": "true",
    }
    response = session.get(url, params=params)
    response.raise_for_status()
    return list(response.json()["workflow_runs"])


def fetch_run_jobs(
    session: requests.Session, repo_full_name: str, run_id: int
) -> list[dict[str, Any]]:
    url = f"{API_ROOT}/repos/{repo_full_name}/actions/runs/{run_id}/jobs"
    params: dict[str, str | int] = {"per_page": 100, "filter": "latest"}
    response = session.get(url, params=params)
    response.raise_for_status()
    return list(response.json()["jobs"])


def load_test_metrics(
    session: requests.Session,
    repo_full_name: str,
    run_id: int,
    artifacts_dir: str | None,
) -> TestMetrics:
    local_metrics = load_local_test_metrics(run_id, artifacts_dir)
    if local_metrics is not None:
        return local_metrics

    artifact = find_test_artifact(session, repo_full_name, run_id)
    if artifact is None:
        return TestMetrics(None, None, None, None, None)

    with tempfile.TemporaryDirectory() as temp_dir:
        zip_path = Path(temp_dir) / "artifact.zip"
        download_artifact(session, repo_full_name, artifact["id"], zip_path)
        with zipfile.ZipFile(zip_path) as archive:
            for name in archive.namelist():
                if name.endswith("pytest-results.xml"):
                    content = archive.read(name)
                    return parse_junit_xml_bytes(content)
    return TestMetrics(None, None, None, None, None)


def load_local_test_metrics(run_id: int, artifacts_dir: str | None) -> TestMetrics | None:
    if artifacts_dir is None:
        return None
    base = Path(artifacts_dir)
    candidates = list(base.glob(f"**/*{run_id}*/pytest-results.xml")) + list(
        base.glob("**/pytest-results.xml")
    )
    if not candidates:
        return None
    return parse_junit_xml_path(candidates[0])


def collect_local_artifacts(artifacts_dir: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for metadata_path in sorted(artifacts_dir.glob("test-results-*/artifacts/run-metadata.json")):
        base_dir = metadata_path.parents[1]
        xml_path = base_dir / "artifacts" / "pytest-results.xml"
        if not xml_path.exists():
            continue
        metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
        metrics = parse_junit_xml_path(xml_path)
        rows.append(
            {
                "run_id": metadata.get("github_run_id"),
                "commit_sha": metadata.get("github_sha"),
                "commit_message": "",
                "status": infer_status_from_tests(metrics),
                "workflow_duration": None,
                "job_name": "tests",
                "job_status": infer_status_from_tests(metrics),
                "job_duration": None,
                "test_count": metrics.test_count,
                "test_failures": metrics.test_failures,
                "test_errors": metrics.test_errors,
                "test_skipped": metrics.test_skipped,
                "test_time_seconds": metrics.test_time_seconds,
                "average_test_seconds": metrics.average_test_seconds,
                "timestamp": metadata.get("generated_at"),
                "event": "local_artifact",
                "cache_mode": metadata.get("cache_mode"),
                "execution_mode": metadata.get("execution_mode"),
                "test_profile": metadata.get("test_profile"),
                "pytest_workers": metadata.get("pytest_workers"),
                "artifact_dir": str(base_dir),
            }
        )
    return rows


def infer_status_from_tests(metrics: TestMetrics) -> str:
    failures = metrics.test_failures or 0
    errors = metrics.test_errors or 0
    if failures + errors > 0:
        return "failure"
    return "success"


def find_test_artifact(
    session: requests.Session, repo_full_name: str, run_id: int
) -> dict[str, Any] | None:
    url = f"{API_ROOT}/repos/{repo_full_name}/actions/runs/{run_id}/artifacts"
    response = session.get(url, params={"per_page": 100})
    response.raise_for_status()
    for artifact in response.json()["artifacts"]:
        if artifact["name"].startswith("test-results-"):
            return dict(artifact)
    return None


def download_artifact(
    session: requests.Session, repo_full_name: str, artifact_id: int, output_path: Path
) -> None:
    url = f"{API_ROOT}/repos/{repo_full_name}/actions/artifacts/{artifact_id}/zip"
    response = session.get(url)
    response.raise_for_status()
    output_path.write_bytes(response.content)


def parse_junit_xml_bytes(content: bytes) -> TestMetrics:
    with io.BytesIO(content) as buffer:
        xml = JUnitXml.fromfile(buffer)
    return junit_to_metrics(xml)


def parse_junit_xml_path(path: Path) -> TestMetrics:
    xml = JUnitXml.fromfile(str(path))
    return junit_to_metrics(xml)


def junit_to_metrics(xml: JUnitXml) -> TestMetrics:
    test_count = int(xml.tests)
    failures = int(xml.failures)
    errors = int(xml.errors)
    skipped = int(xml.skipped)
    test_time = float(xml.time or 0)
    return TestMetrics(test_count, failures, errors, skipped, test_time)


def infer_variant(run: dict[str, Any], commit_summary: str) -> dict[str, str]:
    name = run.get("name") or ""
    display_title = run.get("display_title") or ""
    event = run.get("event") or ""
    lower_text = f"{name} {display_title} {commit_summary}".lower()
    return {
        "event": event,
        "cache_mode": infer_token(
            lower_text, ["enabled", "disabled", "cache-on", "cache-off"], "unknown"
        ),
        "execution_mode": infer_token(lower_text, ["sequential", "parallel"], "unknown"),
        "test_profile": infer_token(
            lower_text, ["fast", "expanded", "slow", "failing"], "unknown"
        ),
    }


def infer_token(text: str, tokens: list[str], default: str) -> str:
    for token in tokens:
        if token in text:
            return (
                token.replace("cache-on", "enabled")
                .replace("cache-off", "disabled")
                .replace("workers-", "")
            )
    return default


def parse_github_datetime(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00")).astimezone(UTC)


def duration_seconds(started_at: datetime, completed_at: datetime) -> float:
    return max((completed_at - started_at).total_seconds(), 0.0)


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    with path.open("w", newline="", encoding="utf-8") as output:
        writer = csv.DictWriter(output, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True), encoding="utf-8")


if __name__ == "__main__":
    raise SystemExit(main())
