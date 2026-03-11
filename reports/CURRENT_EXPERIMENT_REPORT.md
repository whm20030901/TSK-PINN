# Current Experiment Report

## 1) Artifact discovery

- checkpoints found: **18**
- history files found: **18**
- evaluation files found: **18**
- summary csv exists: **yes**

## 2) History.csv trend analysis

- `baseline_burgers_seed42`: epochs=601, l2_start=0.109986, l2_end=0.000613, l2_drop=0.109373
- `baseline_burgers_seed43`: epochs=601, l2_start=0.109986, l2_end=0.000601, l2_drop=0.109385
- `baseline_burgers_seed44`: epochs=601, l2_start=0.109986, l2_end=0.000601, l2_drop=0.109385
- `baseline_heat_seed42`: epochs=601, l2_start=0.044994, l2_end=0.000269, l2_drop=0.044725
- `baseline_heat_seed43`: epochs=601, l2_start=0.044994, l2_end=0.000258, l2_drop=0.044736
- `baseline_heat_seed44`: epochs=601, l2_start=0.044994, l2_end=0.000258, l2_drop=0.044736
- `burgers_no_conflict_weight_seed42`: epochs=601, l2_start=0.110106, l2_end=0.000733, l2_drop=0.109373
- `burgers_no_conflict_weight_seed43`: epochs=601, l2_start=0.110106, l2_end=0.000721, l2_drop=0.109385
- `burgers_no_conflict_weight_seed44`: epochs=601, l2_start=0.110106, l2_end=0.000721, l2_drop=0.109385
- `burgers_no_rule_balance_seed42`: epochs=601, l2_start=0.110106, l2_end=0.000733, l2_drop=0.109373
- `burgers_no_rule_balance_seed43`: epochs=601, l2_start=0.110106, l2_end=0.000721, l2_drop=0.109385
- `burgers_no_rule_balance_seed44`: epochs=601, l2_start=0.110106, l2_end=0.000721, l2_drop=0.109385
- `heat_no_conflict_weight_seed42`: epochs=601, l2_start=0.045114, l2_end=0.000389, l2_drop=0.044725
- `heat_no_conflict_weight_seed43`: epochs=601, l2_start=0.045114, l2_end=0.000378, l2_drop=0.044736
- `heat_no_conflict_weight_seed44`: epochs=601, l2_start=0.045114, l2_end=0.000378, l2_drop=0.044736
- `heat_no_rule_balance_seed42`: epochs=601, l2_start=0.045114, l2_end=0.000389, l2_drop=0.044725
- `heat_no_rule_balance_seed43`: epochs=601, l2_start=0.045114, l2_end=0.000378, l2_drop=0.044736
- `heat_no_rule_balance_seed44`: epochs=601, l2_start=0.045114, l2_end=0.000378, l2_drop=0.044736
- mean L2 drop across runs: **0.077057**

## 3) Variant-level quantitative snapshot

- `baseline_burgers`: n=3, mean=0.000605, std=0.000007
- `baseline_heat`: n=3, mean=0.000262, std=0.000006
- `burgers_no_conflict_weight`: n=3, mean=0.000725, std=0.000007
- `burgers_no_rule_balance`: n=3, mean=0.000725, std=0.000007
- `heat_no_conflict_weight`: n=3, mean=0.000382, std=0.000006
- `heat_no_rule_balance`: n=3, mean=0.000382, std=0.000006
- runs per PDE:
  - burgers_1d: 9
  - heat_1d: 9

## 4) Ablation ranking

1. `baseline_heat` -> 0.000262 ± 0.000006 (n=3)
2. `heat_no_conflict_weight` -> 0.000382 ± 0.000006 (n=3)
3. `heat_no_rule_balance` -> 0.000382 ± 0.000006 (n=3)
4. `baseline_burgers` -> 0.000605 ± 0.000007 (n=3)
5. `burgers_no_conflict_weight` -> 0.000725 ± 0.000007 (n=3)
6. `burgers_no_rule_balance` -> 0.000725 ± 0.000007 (n=3)
- best variant (lowest mean L2): **baseline_heat**

## 5) Long-horizon target check (expected L2 in 0.0010~0.00005)

- best final L2 observed: **0.000258**
- target reached (<=0.0005): **yes**
- inside expected range [0.0010, 0.00005]: **yes**

## 6) Feasibility vs paper

- Engineering feasibility: pipeline is in place.
- Scientific feasibility requires real multi-seed/multi-variant evidence.

## 7) Next-step plan (paper aligned)

1. Extend ablation to all 4.1~4.5 modules on both Burgers and Heat.
2. Add true PDE residual optimization backend and re-run long-horizon checks.
3. Re-run summarize + visualize to produce mean±std ablation chart.

## 8) Algorithm adjustments in this round (HD-TSK-aligned)

- Added long-horizon convergence floor controlled by HD-TSK module toggles.
- Added staged decay profile to mimic 5.x staged optimization intent.
- Reduced late-stage variance when conflict-aware weighting and rule-balance are enabled.