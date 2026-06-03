from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any, cast

import matplotlib.pyplot as plt
import pandas as pd


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate CI/CD metric charts.")
    parser.add_argument("--input", default="data/pipeline_metrics.csv")
    parser.add_argument("--output-dir", default="charts")
    args = parser.parse_args()

    data = pd.read_csv(args.input)
    if data.empty:
        raise SystemExit("Input dataset is empty.")

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    runs = data.drop_duplicates(subset=["run_id"]).sort_values("timestamp")
    plot_workflow_duration(runs, output_dir / "workflow_duration_by_run.png")
    plot_job_duration(data, output_dir / "job_duration_by_name.png")
    plot_status_rate(runs, output_dir / "success_failure_rate.png")
    plot_tests_vs_duration(runs, output_dir / "tests_vs_duration.png")

    print(f"Wrote charts to {output_dir}")
    return 0


def plot_workflow_duration(runs: pd.DataFrame, output: Path) -> None:
    plt.figure(figsize=(11, 6))
    labels = runs["run_number"].astype(str)
    plt.plot(labels, runs["workflow_duration"], marker="o")
    plt.title("Tempo total do pipeline por execucao")
    plt.xlabel("Numero da execucao")
    plt.ylabel("Duracao do workflow (s)")
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(output, dpi=160)
    plt.close()


def plot_job_duration(data: pd.DataFrame, output: Path) -> None:
    grouped = cast(Any, data.groupby("job_name", as_index=False)["job_duration"].mean())
    grouped = grouped.sort_values("job_duration", ascending=False)
    plt.figure(figsize=(10, 6))
    plt.bar(grouped["job_name"], grouped["job_duration"])
    plt.title("Tempo medio por job")
    plt.xlabel("Job")
    plt.ylabel("Duracao media (s)")
    plt.xticks(rotation=30, ha="right")
    plt.tight_layout()
    plt.savefig(output, dpi=160)
    plt.close()


def plot_status_rate(runs: pd.DataFrame, output: Path) -> None:
    counts = runs["status"].fillna("unknown").value_counts()
    plt.figure(figsize=(8, 6))
    plt.pie(
        counts.to_numpy(),
        labels=[str(label) for label in counts.index.tolist()],
        autopct="%1.1f%%",
        startangle=90,
    )
    plt.title("Taxa de sucesso e falha")
    plt.tight_layout()
    plt.savefig(output, dpi=160)
    plt.close()


def plot_tests_vs_duration(runs: pd.DataFrame, output: Path) -> None:
    plt.figure(figsize=(9, 6))
    colors = runs["status"].map({"success": "tab:green", "failure": "tab:red"}).fillna("tab:gray")
    plt.scatter(runs["test_count"], runs["workflow_duration"], c=colors)
    plt.title("Relacao entre quantidade de testes e duracao do pipeline")
    plt.xlabel("Quantidade de testes")
    plt.ylabel("Duracao do workflow (s)")
    plt.tight_layout()
    plt.savefig(output, dpi=160)
    plt.close()


if __name__ == "__main__":
    raise SystemExit(main())
