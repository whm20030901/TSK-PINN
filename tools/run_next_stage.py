#!/usr/bin/env python3
from __future__ import annotations

import argparse
import subprocess
from pathlib import Path


EXPERIMENT_MATRIX = [
    ("configs/base.yaml", "baseline_burgers"),
    ("configs/ablation/no_conflict_weight.yaml", "no_conflict_weight"),
    ("configs/ablation/no_rule_balance.yaml", "no_rule_balance"),
]


def run(cmd: list[str]) -> None:
    print("[cmd]", " ".join(cmd))
    subprocess.run(cmd, check=True)


def main() -> None:
    p = argparse.ArgumentParser(description="Run the next-stage multi-seed ablation batch.")
    p.add_argument("--seeds", default="42,43,44", help="comma-separated seeds")
    p.add_argument("--runs-dir", default="runs")
    p.add_argument("--summary-csv", default="results/raw/summary.csv")
    p.add_argument("--figures-dir", default="results/figures")
    p.add_argument("--report", default="reports/CURRENT_EXPERIMENT_REPORT.md")
    p.add_argument("--stage", default="reports/EXPERIMENT_STAGE.md")
    args = p.parse_args()

    seeds = [int(x.strip()) for x in args.seeds.split(",") if x.strip()]

    for config, variant in EXPERIMENT_MATRIX:
        for seed in seeds:
            run_name = f"{variant}_seed{seed}"
            run([
                "python",
                "train.py",
                "--config",
                config,
                "--run-name",
                run_name,
                "--seed",
                str(seed),
            ])
            ckpt = str(Path(args.runs_dir) / run_name / "checkpoint.json")
            run([
                "python",
                "evaluate.py",
                "--config",
                config,
                "--ckpt",
                ckpt,
            ])

    run(["python", "tools/summarize.py", "--runs-dir", args.runs_dir, "--out", args.summary_csv])
    run([
        "python",
        "tools/visualize.py",
        "--run-dir",
        args.runs_dir,
        "--summary-csv",
        args.summary_csv,
        "--out-dir",
        args.figures_dir,
        "--run-name",
        f"baseline_burgers_seed{seeds[0]}",
    ])
    run([
        "python",
        "tools/analyze_results.py",
        "--runs-dir",
        args.runs_dir,
        "--summary-csv",
        args.summary_csv,
        "--out",
        args.report,
        "--stage-out",
        args.stage,
    ])

    print("[done] next-stage batch completed")


if __name__ == "__main__":
    main()
