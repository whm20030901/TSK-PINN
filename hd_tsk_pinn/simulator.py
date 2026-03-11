from __future__ import annotations

from dataclasses import dataclass
import math
import random
from typing import Dict


@dataclass
class ModuleToggles:
    hierarchical_antecedent: bool = True
    adapter_consequent: bool = True
    difficulty_score: bool = True
    rule_balance_reg: bool = True
    conflict_aware_weighting: bool = True


def _module_gain(t: ModuleToggles) -> float:
    gain = 0.0
    gain += 0.08 if t.hierarchical_antecedent else 0.0
    gain += 0.06 if t.adapter_consequent else 0.0
    gain += 0.07 if t.difficulty_score else 0.0
    gain += 0.04 if t.rule_balance_reg else 0.0
    gain += 0.05 if t.conflict_aware_weighting else 0.0
    return gain


def run_simulated_training(cfg: Dict, epochs: int) -> Dict:
    seed = int(cfg["runtime"]["seed"])
    random.seed(seed)

    t = ModuleToggles(**cfg["modules"])
    gain = _module_gain(t)

    pde = cfg["pde"]["name"]
    baseline = {"burgers_1d": 0.11, "heat_1d": 0.045}.get(pde, 0.1)
    noise = random.uniform(-0.005, 0.005)
    target_error = max(0.004, baseline * (1 - gain) + noise)

    losses = []
    for epoch in range(1, epochs + 1):
        decay = math.exp(-epoch / max(epochs / 6, 1))
        l2 = target_error + (baseline - target_error) * decay
        residual = l2 * random.uniform(0.7, 1.3)
        bc_ic = l2 * random.uniform(0.4, 0.9)
        losses.append({
            "epoch": epoch,
            "l2_error": round(l2, 6),
            "pde_residual": round(residual, 6),
            "bc_ic_error": round(bc_ic, 6),
        })

    final = losses[-1]
    params = (
        cfg["model"]["backbone_width"] * cfg["model"]["backbone_depth"] * 100
        + cfg["model"]["k_coarse"] * cfg["model"]["k_fine"] * 10
    )
    if t.adapter_consequent:
        params = int(params * 0.72)

    return {
        "history": losses,
        "final": final,
        "estimated_params": params,
        "estimated_epoch_seconds": round(0.08 + params / 2_000_000, 4),
    }
