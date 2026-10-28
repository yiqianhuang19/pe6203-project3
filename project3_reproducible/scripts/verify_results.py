"""Check internal consistency of the packaged Project 3 result files.

This script is read-only: it neither calls a model nor requires an API key.
"""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SUMMARIES = ROOT / "results" / "summaries"
FINAL_RUNS = ROOT / "results" / "final_runs"


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> None:
    required = [
        "baseline_batch_summary.json",
        "random_search_batch_summary.json",
        "bayesian_optimization_batch_summary.json",
        "custom_cost_aware_batch_summary.json",
        "final_config_selection.json",
        "hpo_protocol_frozen.json",
    ]
    missing = [name for name in required if not (SUMMARIES / name).exists()]
    if missing:
        raise SystemExit(f"Missing required summary files: {missing}")

    selection = load(SUMMARIES / "final_config_selection.json")
    frozen = selection["frozen_final_config"]
    if frozen["label"] != "final_c0_off_default":
        raise SystemExit(f"Unexpected frozen configuration: {frozen}")

    test_files = sorted(FINAL_RUNS.glob("*_final_summary.json"))
    if len(test_files) != 2:
        raise SystemExit(f"Expected two held-out summaries, found {len(test_files)}")

    tests = [load(path) for path in test_files]
    failed = [item["task"] for item in tests if item.get("pass_at_1") != 1]
    if failed:
        raise SystemExit(f"Held-out task(s) did not pass: {failed}")

    print("OK: six summary files are present.")
    print("OK: final configuration is final_c0_off_default.")
    print("OK: held-out pass@1 = 2/2 = 1.0.")


if __name__ == "__main__":
    main()
