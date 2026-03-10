#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
from pathlib import Path
from typing import Dict, List, Tuple


def _read_history(path: Path) -> List[Dict[str, float]]:
    rows: List[Dict[str, float]] = []
    with path.open("r", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            rows.append(
                {
                    "epoch": float(row["epoch"]),
                    "l2_error": float(row["l2_error"]),
                    "pde_residual": float(row["pde_residual"]),
                    "bc_ic_error": float(row["bc_ic_error"]),
                }
            )
    return rows


def _read_summary(path: Path) -> List[Dict[str, str]]:
    with path.open("r", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def _polyline(points: List[Tuple[float, float]], color: str, stroke: int = 2) -> str:
    p = " ".join(f"{x:.2f},{y:.2f}" for x, y in points)
    return f'<polyline fill="none" stroke="{color}" stroke-width="{stroke}" points="{p}" />'


def _scale(v: float, in_min: float, in_max: float, out_min: float, out_max: float) -> float:
    if abs(in_max - in_min) < 1e-12:
        return (out_min + out_max) / 2
    ratio = (v - in_min) / (in_max - in_min)
    return out_min + ratio * (out_max - out_min)


def plot_loss_svg(history_csv: Path, out_svg: Path) -> None:
    rows = _read_history(history_csv)
    if not rows:
        raise ValueError(f"No rows in {history_csv}")

    w, h = 960, 540
    ml, mr, mt, mb = 90, 40, 40, 70
    cw, ch = w - ml - mr, h - mt - mb

    xs = [r["epoch"] for r in rows]
    ys = [r["l2_error"] for r in rows] + [r["pde_residual"] for r in rows] + [r["bc_ic_error"] for r in rows]
    xmin, xmax = min(xs), max(xs)
    ymin, ymax = min(ys), max(ys)

    def points(metric: str) -> List[Tuple[float, float]]:
        return [
            (
                _scale(r["epoch"], xmin, xmax, ml, ml + cw),
                _scale(r[metric], ymin, ymax, mt + ch, mt),
            )
            for r in rows
        ]

    grid = []
    for i in range(6):
        y = mt + (ch / 5) * i
        grid.append(f'<line x1="{ml}" y1="{y:.2f}" x2="{ml+cw}" y2="{y:.2f}" stroke="#eaeaea" />')

    content = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}">',
        '<rect width="100%" height="100%" fill="white" />',
        *grid,
        f'<line x1="{ml}" y1="{mt+ch}" x2="{ml+cw}" y2="{mt+ch}" stroke="#333" />',
        f'<line x1="{ml}" y1="{mt}" x2="{ml}" y2="{mt+ch}" stroke="#333" />',
        _polyline(points("l2_error"), "#1f77b4"),
        _polyline(points("pde_residual"), "#d62728"),
        _polyline(points("bc_ic_error"), "#2ca02c"),
        f'<text x="{w/2:.0f}" y="24" text-anchor="middle" font-size="20">Training Curves (PINN-style)</text>',
        f'<text x="{w/2:.0f}" y="{h-18}" text-anchor="middle" font-size="14">Epoch</text>',
        f'<text x="24" y="{h/2:.0f}" transform="rotate(-90,24,{h/2:.0f})" text-anchor="middle" font-size="14">Error</text>',
        '<rect x="700" y="70" width="14" height="4" fill="#1f77b4" /><text x="720" y="74" font-size="12">L2</text>',
        '<rect x="700" y="95" width="14" height="4" fill="#d62728" /><text x="720" y="99" font-size="12">PDE residual</text>',
        '<rect x="700" y="120" width="14" height="4" fill="#2ca02c" /><text x="720" y="124" font-size="12">BC/IC error</text>',
        '</svg>',
    ]
    out_svg.parent.mkdir(parents=True, exist_ok=True)
    out_svg.write_text("\n".join(content), encoding="utf-8")


def plot_ablation_svg(summary_csv: Path, out_svg: Path) -> None:
    rows = _read_summary(summary_csv)
    if not rows:
        raise ValueError(f"No rows in {summary_csv}")

    data = [(r["run"], float(r["l2_error"])) for r in rows]
    w, h = 960, 540
    ml, mr, mt, mb = 80, 40, 40, 120
    cw, ch = w - ml - mr, h - mt - mb

    max_v = max(v for _, v in data) * 1.1
    bw = cw / max(len(data), 1) * 0.6
    gap = cw / max(len(data), 1) * 0.4

    bars = []
    labels = []
    x = ml + gap / 2
    palette = ["#4e79a7", "#f28e2b", "#e15759", "#76b7b2", "#59a14f", "#edc949"]
    for i, (name, value) in enumerate(data):
        bar_h = _scale(value, 0, max_v, 0, ch)
        y = mt + ch - bar_h
        color = palette[i % len(palette)]
        bars.append(f'<rect x="{x:.2f}" y="{y:.2f}" width="{bw:.2f}" height="{bar_h:.2f}" fill="{color}" />')
        bars.append(f'<text x="{x+bw/2:.2f}" y="{y-6:.2f}" text-anchor="middle" font-size="11">{value:.4f}</text>')
        labels.append(f'<text x="{x+bw/2:.2f}" y="{h-30}" transform="rotate(20,{x+bw/2:.2f},{h-30})" text-anchor="start" font-size="11">{name}</text>')
        x += bw + gap

    content = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}">',
        '<rect width="100%" height="100%" fill="white" />',
        f'<line x1="{ml}" y1="{mt+ch}" x2="{ml+cw}" y2="{mt+ch}" stroke="#333" />',
        f'<line x1="{ml}" y1="{mt}" x2="{ml}" y2="{mt+ch}" stroke="#333" />',
        *bars,
        *labels,
        f'<text x="{w/2:.0f}" y="24" text-anchor="middle" font-size="20">Ablation Comparison (L2 Error)</text>',
        f'<text x="{w/2:.0f}" y="{h-8}" text-anchor="middle" font-size="14">Runs</text>',
        f'<text x="24" y="{h/2:.0f}" transform="rotate(-90,24,{h/2:.0f})" text-anchor="middle" font-size="14">L2 Error</text>',
        '</svg>',
    ]
    out_svg.parent.mkdir(parents=True, exist_ok=True)
    out_svg.write_text("\n".join(content), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate experiment visualizations.")
    parser.add_argument("--run-dir", default="runs", help="runs root")
    parser.add_argument("--summary-csv", default="results/raw/summary.csv")
    parser.add_argument("--out-dir", default="results/figures")
    parser.add_argument("--run-name", default="", help="optional run name for loss curve")
    args = parser.parse_args()

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    run_dir = Path(args.run_dir)
    if args.run_name:
        history_csv = run_dir / args.run_name / "history.csv"
    else:
        candidates = sorted(run_dir.glob("*/history.csv"))
        if not candidates:
            raise FileNotFoundError("No history.csv found under runs")
        history_csv = candidates[-1]

    loss_svg = out_dir / "loss_curves.svg"
    ablation_svg = out_dir / "ablation_l2.svg"
    plot_loss_svg(history_csv, loss_svg)
    plot_ablation_svg(Path(args.summary_csv), ablation_svg)

    print(f"[viz] loss curve: {loss_svg}")
    print(f"[viz] ablation chart: {ablation_svg}")


if __name__ == "__main__":
    main()
