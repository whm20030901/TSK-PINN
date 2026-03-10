#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

from hd_tsk_pinn.config import load_config


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", required=True)
    parser.add_argument("--ckpt", required=True)
    args = parser.parse_args()

    _ = load_config(args.config)  # ensures config is valid and loadable
    ckpt = json.loads(Path(args.ckpt).read_text(encoding="utf-8"))
    metrics = ckpt["metrics"]

    out_csv = Path(args.ckpt).parent / "evaluation.csv"
    with out_csv.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(metrics.keys()))
        writer.writeheader()
        writer.writerow(metrics)

    print(f"[eval] metrics={metrics}")
    print(f"[eval] output={out_csv}")


if __name__ == "__main__":
    main()
