#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
from pathlib import Path
from statistics import mean, stdev
from typing import Dict, List


def read_csv(path: Path):
    with path.open("r", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def _read_history_metrics(history_csv: Path) -> Dict[str, float]:
    rows = read_csv(history_csv)
    if not rows:
        return {}
    l2 = [float(r["l2_error"]) for r in rows]
    pde = [float(r["pde_residual"]) for r in rows]
    bc = [float(r["bc_ic_error"]) for r in rows]
    return {
        "epochs": len(rows),
        "l2_start": l2[0],
        "l2_end": l2[-1],
        "l2_drop": l2[0] - l2[-1],
        "pde_mean": mean(pde),
        "bc_mean": mean(bc),
    }


def _infer_stage(n_hist: int, n_variants: int, n_seeds_max: int) -> str:
    if n_hist == 0:
        return "Stage 1 - Reproducible scaffold ready (no completed runs in current workspace)"
    if n_variants <= 1:
        return "Stage 2 - Single-baseline running"
    if n_seeds_max < 3:
        return "Stage 3 - Multi-variant ablation started (seed count insufficient for stable statistics)"
    return "Stage 4 - Paper-aligned ablation with statistical support"


def main() -> None:
    p = argparse.ArgumentParser(description="Analyze experiment artifacts and generate markdown report + stage tracker.")
    p.add_argument("--runs-dir", default="runs")
    p.add_argument("--summary-csv", default="results/raw/summary.csv")
    p.add_argument("--out", default="reports/CURRENT_EXPERIMENT_REPORT.md")
    p.add_argument("--stage-out", default="reports/EXPERIMENT_STAGE.md")
    args = p.parse_args()

    runs_dir = Path(args.runs_dir)
    summary_csv = Path(args.summary_csv)
    out = Path(args.out)
    stage_out = Path(args.stage_out)

    ckpts = sorted(runs_dir.glob("*/checkpoint.json"))
    evals = sorted(runs_dir.glob("*/evaluation.csv"))
    hists = sorted(runs_dir.glob("*/history.csv"))

    # summary-level aggregation
    variants: Dict[str, List[float]] = {}
    pde_counts: Dict[str, int] = {}
    if summary_csv.exists():
        for r in read_csv(summary_csv):
            run = r.get("run", "")
            variant = run.rsplit("_seed", 1)[0] if "_seed" in run else run
            try:
                variants.setdefault(variant, []).append(float(r["l2_error"]))
            except Exception:
                continue
            pde = r.get("pde", "unknown")
            pde_counts[pde] = pde_counts.get(pde, 0) + 1

    history_metrics = []
    for h in hists:
        m = _read_history_metrics(h)
        if m:
            history_metrics.append((h.parent.name, m))

    n_variants = len(variants)
    n_seeds_max = max((len(v) for v in variants.values()), default=0)
    stage = _infer_stage(len(hists), n_variants, n_seeds_max)

    lines = [
        "# Current Experiment Report",
        "",
        "## 1) Artifact discovery",
        "",
        f"- checkpoints found: **{len(ckpts)}**",
        f"- history files found: **{len(hists)}**",
        f"- evaluation files found: **{len(evals)}**",
        f"- summary csv exists: **{'yes' if summary_csv.exists() else 'no'}**",
        "",
    ]

    lines += ["## 2) History.csv trend analysis", ""]
    if history_metrics:
        for run, m in history_metrics:
            lines.append(f"- `{run}`: epochs={int(m['epochs'])}, l2_start={m['l2_start']:.6f}, l2_end={m['l2_end']:.6f}, l2_drop={m['l2_drop']:.6f}")
        avg_drop = mean(m["l2_drop"] for _, m in history_metrics)
        lines.append(f"- mean L2 drop across runs: **{avg_drop:.6f}**")
    else:
        lines.append("- 未在当前工作区检测到 `runs/*/history.csv`，无法完成你要求的历史曲线定量分析。")
    lines.append("")

    lines += ["## 3) Variant-level quantitative snapshot", ""]
    ranked = []
    if variants:
        for k, vals in sorted(variants.items()):
            v_mean = mean(vals)
            v_std = stdev(vals) if len(vals) > 1 else 0.0
            ranked.append((k, v_mean, v_std, len(vals)))
            msg = f"- `{k}`: n={len(vals)}, mean={v_mean:.6f}"
            if len(vals) > 1:
                msg += f", std={v_std:.6f}"
            lines.append(msg)
        ranked.sort(key=lambda x: x[1])
        lines.append("- runs per PDE:")
        for pde, c in sorted(pde_counts.items()):
            lines.append(f"  - {pde}: {c}")
    else:
        lines.append("- No variant metrics parsed from summary.csv.")
    lines.append("")

    lines += ["## 4) Ablation ranking", ""]
    if ranked:
        for i, (name, m, sd, n) in enumerate(ranked, start=1):
            tail = f" ± {sd:.6f}" if n > 1 else ""
            lines.append(f"{i}. `{name}` -> {m:.6f}{tail} (n={n})")
        lines.append(f"- best variant (lowest mean L2): **{ranked[0][0]}**")
    else:
        lines.append("- ranking unavailable (no summary rows).")
    lines.append("")

    lines += [
        "## 5) Feasibility vs paper",
        "",
        "- Engineering feasibility: pipeline is in place.",
        "- Scientific feasibility requires real multi-seed/multi-variant evidence.",
        "",
        "## 6) Next-step plan (paper aligned)",
        "",
        "1. Ensure `runs/*/history.csv` and `results/raw/summary.csv` are synced into this branch.",
        "2. Run baseline + no_conflict_weight + no_rule_balance with seeds 42/43/44.",
        "3. Re-run summarize + visualize to produce mean±std ablation chart.",
    ]

    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("\n".join(lines), encoding="utf-8")

    stage_lines = [
        "# Experiment Stage Tracker",
        "",
        f"- Current Stage: **{stage}**",
        f"- Histories detected: {len(hists)}",
        f"- Variants detected: {n_variants}",
        f"- Max seeds per variant: {n_seeds_max}",
        "",
        "## Stage definition",
        "- Stage 1: Scaffold ready, no completed runs in current workspace.",
        "- Stage 2: Single baseline run available.",
        "- Stage 3: Multi-variant ablation started, but seed count < 3.",
        "- Stage 4: Multi-variant with >=3 seeds, ready for stronger paper claims.",
    ]
    stage_out.parent.mkdir(parents=True, exist_ok=True)
    stage_out.write_text("\n".join(stage_lines), encoding="utf-8")

    print(f"[report] wrote {out}")
    print(f"[stage] wrote {stage_out}")


if __name__ == "__main__":
    main()
