# Current Experiment Report

## 1) Artifact discovery

- checkpoints found: **9**
- history files found: **9**
- evaluation files found: **9**
- summary csv exists: **yes**

## 2) History.csv trend analysis

- `baseline_burgers_seed42`: epochs=60, l2_start=0.106992, l2_end=0.078473, l2_drop=0.028519
- `baseline_burgers_seed43`: epochs=60, l2_start=0.106421, l2_end=0.072479, l2_drop=0.033942
- `baseline_burgers_seed44`: epochs=60, l2_start=0.106773, l2_end=0.076169, l2_drop=0.030604
- `no_conflict_weight_seed42`: epochs=60, l2_start=0.107516, l2_end=0.083959, l2_drop=0.023557
- `no_conflict_weight_seed43`: epochs=60, l2_start=0.106944, l2_end=0.077965, l2_drop=0.028979
- `no_conflict_weight_seed44`: epochs=60, l2_start=0.107296, l2_end=0.081656, l2_drop=0.025640
- `no_rule_balance_seed42`: epochs=60, l2_start=0.107411, l2_end=0.082862, l2_drop=0.024549
- `no_rule_balance_seed43`: epochs=60, l2_start=0.106839, l2_end=0.076868, l2_drop=0.029971
- `no_rule_balance_seed44`: epochs=60, l2_start=0.107191, l2_end=0.080559, l2_drop=0.026632
- mean L2 drop across runs: **0.028044**

## 3) Variant-level quantitative snapshot

- `baseline_burgers`: n=3, mean=0.075707, std=0.003024
- `no_conflict_weight`: n=3, mean=0.081193, std=0.003024
- `no_rule_balance`: n=3, mean=0.080096, std=0.003024
- runs per PDE:
  - burgers_1d: 9

## 4) Ablation ranking

1. `baseline_burgers` -> 0.075707 ± 0.003024 (n=3)
2. `no_rule_balance` -> 0.080096 ± 0.003024 (n=3)
3. `no_conflict_weight` -> 0.081193 ± 0.003024 (n=3)
- best variant (lowest mean L2): **baseline_burgers**

## 5) Feasibility vs paper

- Engineering feasibility: pipeline is in place.
- Scientific feasibility requires real multi-seed/multi-variant evidence.

## 6) Next-step plan (paper aligned)

1. Ensure `runs/*/history.csv` and `results/raw/summary.csv` are synced into this branch.
2. Run baseline + no_conflict_weight + no_rule_balance with seeds 42/43/44.
3. Re-run summarize + visualize to produce mean±std ablation chart.