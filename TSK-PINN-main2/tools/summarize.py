#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--runs-dir", default="runs")
    parser.add_argument("--out", default="results/raw/summary.csv")
    args = parser.parse_args()

    runs_dir = Path(args.runs_dir)
    rows = []
    for ckpt in runs_dir.glob("*/checkpoint.json"):
        data = json.loads(ckpt.read_text(encoding="utf-8"))
        m = data["metrics"]
        rows.append({
            "run": ckpt.parent.name,
            "pde": data["config"]["pde"]["name"],
            "seed": data["config"]["runtime"]["seed"],
            "l2_error": m["l2_error"],
            "pde_residual": m["pde_residual"],
            "bc_ic_error": m["bc_ic_error"],
            "params": data["estimated_params"],
        })

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["run", "pde", "seed", "l2_error", "pde_residual", "bc_ic_error", "params"])
        writer.writeheader()
        writer.writerows(rows)

    print(f"[summary] wrote {len(rows)} rows to {out}")


if __name__ == "__main__":
    main()
