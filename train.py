#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
from datetime import datetime, UTC
from pathlib import Path
import subprocess

from hd_tsk_pinn.config import load_config
from hd_tsk_pinn.simulator import run_simulated_training


def _git_commit() -> str:
    try:
        return subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip()
    except Exception:
        return "unknown"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", required=True)
    parser.add_argument("--run-name", default="")
    parser.add_argument("--seed", type=int, default=None, help="override runtime.seed from config")
    parser.add_argument("--epochs", type=int, default=None, help="override training.epochs from config")
    args = parser.parse_args()

    cfg = load_config(args.config)
    if args.seed is not None:
        cfg.setdefault("runtime", {})["seed"] = int(args.seed)

    if args.epochs is not None:
        cfg.setdefault("training", {})["epochs"] = int(args.epochs)

    epochs = int(cfg["training"]["epochs"])
    run_name = args.run_name or f"{cfg['pde']['name']}_seed{cfg['runtime']['seed']}"
    run_dir = Path(cfg["runtime"]["runs_dir"]) / run_name
    run_dir.mkdir(parents=True, exist_ok=True)

    result = run_simulated_training(cfg, epochs)

    history_path = run_dir / "history.csv"
    with history_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["epoch", "l2_error", "pde_residual", "bc_ic_error"])
        writer.writeheader()
        writer.writerows(result["history"])

    ckpt = {
        "timestamp": datetime.now(UTC).isoformat(),
        "commit": _git_commit(),
        "config": cfg,
        "metrics": result["final"],
        "estimated_params": result["estimated_params"],
        "estimated_epoch_seconds": result["estimated_epoch_seconds"],
    }
    ckpt_path = run_dir / "checkpoint.json"
    ckpt_path.write_text(json.dumps(ckpt, indent=2), encoding="utf-8")

    print(f"[train] run_dir={run_dir}")
    print(f"[train] checkpoint={ckpt_path}")


if __name__ == "__main__":
    main()
