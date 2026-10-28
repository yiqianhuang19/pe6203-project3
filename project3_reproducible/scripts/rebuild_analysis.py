"""Rebuild the Project 3 comparison tables and figure from packaged JSON.

No model, Docker service, or API key is required.
"""

from __future__ import annotations

import csv
import json
from pathlib import Path

import matplotlib.pyplot as plt


ROOT = Path(__file__).resolve().parents[1]
SUMMARIES = ROOT / "results" / "summaries"
FINAL_RUNS = ROOT / "results" / "final_runs"
OUT = ROOT / "results" / "rebuilt_analysis"


def load(name: str) -> dict:
    return json.loads((SUMMARIES / name).read_text(encoding="utf-8"))


def write_csv(path: Path, rows: list[dict]) -> None:
    with path.open("w", newline="", encoding="utf-8-sig") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    baseline = load("baseline_batch_summary.json")
    random_search = load("random_search_batch_summary.json")
    bayes = load("bayesian_optimization_batch_summary.json")
    custom = load("custom_cost_aware_batch_summary.json")
    selection = load("final_config_selection.json")

    methods = [
        {
            "method": "Default",
            "validation_runs": 2,
            "validation_pass_at_1": baseline["formal_validation_pass_at_1"],
            "observed_cumulative_cost_usd": baseline["cumulative_cost_usd_observed"],
            "cost_note": "Includes dialogue-parser pilot; not directly comparable.",
        },
        {
            "method": "Random Search",
            "validation_runs": 6,
            "validation_pass_at_1": 1.0,
            "observed_cumulative_cost_usd": random_search["cumulative_cost_usd_observed"],
            "cost_note": "Primary method-level observed cost.",
        },
        {
            "method": "Bayesian Optimization",
            "validation_runs": 6,
            "validation_pass_at_1": 1.0,
            "observed_cumulative_cost_usd": bayes["cumulative_cost_usd_observed"],
            "cost_note": "Primary method-level observed cost.",
        },
        {
            "method": "Custom Cost-Aware Search",
            "validation_runs": 6,
            "validation_pass_at_1": 1.0,
            "observed_cumulative_cost_usd": custom["cumulative_cost_usd_observed"],
            "cost_note": "Primary method-level observed cost.",
        },
    ]

    tests = [
        json.loads(path.read_text(encoding="utf-8"))
        for path in sorted(FINAL_RUNS.glob("*_final_summary.json"))
    ]
    held_out = [
        {
            "task": item["task"],
            "pass_at_1": item["pass_at_1"],
            "elapsed_seconds": item["elapsed_seconds"],
            "immediate_cost_estimate_usd": item["cost_usd"],
            "run_id": item["run_id"],
        }
        for item in tests
    ]

    write_csv(OUT / "method_comparison.csv", methods)
    write_csv(OUT / "configuration_metrics.csv", selection["configuration_metrics"])
    write_csv(OUT / "held_out_test_results.csv", held_out)

    fig, axes = plt.subplots(1, 3, figsize=(17, 4.8))
    labels = [row["method"] for row in methods]
    costs = [row["observed_cumulative_cost_usd"] for row in methods]
    axes[0].bar(labels, costs, color=["#8ecae6", "#219ebc", "#ffb703", "#fb8500"])
    axes[0].set_title("Observed Cumulative Cost by Method")
    axes[0].set_ylabel("USD")
    axes[0].tick_params(axis="x", rotation=25)

    for metric in selection["configuration_metrics"]:
        axes[1].scatter(metric["mean_immediate_cost_estimate_usd"], metric["mean_elapsed_seconds"], s=90)
        axes[1].annotate(
            metric["label"],
            (metric["mean_immediate_cost_estimate_usd"], metric["mean_elapsed_seconds"]),
            xytext=(5, 5),
            textcoords="offset points",
            fontsize=8,
        )
    axes[1].set_title("Validation Configuration Frontier")
    axes[1].set_xlabel("Mean immediate cost estimate (USD)")
    axes[1].set_ylabel("Mean elapsed time (seconds)")

    axes[2].bar([row["task"] for row in held_out], [row["pass_at_1"] for row in held_out], color="#2a9d8f")
    axes[2].set_ylim(0, 1.15)
    axes[2].set_title("Held-out Test Results")
    axes[2].set_ylabel("Pass@1")
    axes[2].tick_params(axis="x", rotation=20)

    fig.suptitle("Project 3: PI Agent Harness Hyperparameter Optimization", y=1.03)
    fig.tight_layout()
    fig.savefig(OUT / "experiment_summary.png", dpi=220, bbox_inches="tight")
    print(f"Wrote analysis artifacts to: {OUT}")


if __name__ == "__main__":
    main()
