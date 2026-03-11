# TSK-PINN Experiment Scaffold

## 我现在已经完成了什么（对应论文）

本仓库目前已完成的是 **可执行的实验工程骨架**，用于把论文方法分解成可复现实验流程。

- 已完成训练入口、评估入口、汇总入口：`train.py`、`evaluate.py`、`tools/summarize.py`。
- 已完成配置分层：`configs/base.yaml` + `configs/pde/*.yaml` + `configs/ablation/*.yaml`。
- 已完成实验注册：`experiment_registry.yaml`。
- 已完成结果产物规范：run 目录下 `checkpoint.json`、`history.csv`、`evaluation.csv`，以及汇总 `results/raw/summary.csv`。

### 与论文结构的对应关系

- **论文 4.1 Hierarchical TSK Antecedent**
  - 对应配置开关：`modules.hierarchical_antecedent`
- **论文 4.2 Shared-Backbone Adapter Consequents**
  - 对应配置开关：`modules.adapter_consequent`
- **论文 4.3 Region-Level Difficulty Scoring and Rule Evolution**
  - 对应配置开关：`modules.difficulty_score`
- **论文 4.4 Rule-Balance Regularization**
  - 对应配置开关：`modules.rule_balance_reg`
- **论文 4.5 Gradient-Conflict-Aware Task Weighting**
  - 对应配置开关：`modules.conflict_aware_weighting`
- **论文 5.x Training Algorithm / Cost**
  - 对应：训练配置与阶段优化器字段（`optimizer_stage1`, `optimizer_stage2`）及 checkpoint 中的参数量/耗时记录
- **论文 6.x Experiments（Implementation/Baselines/Results/Ablation）**
  - 对应：PDE 配置、ablation 配置、评估输出与跨运行汇总脚本

> 说明：当前版本优先完成“实验流水线与可复现框架”，便于快速开展 4.x 模块的真实数值实现与对照实验。

## Quick start

```bash
python train.py --config configs/base.yaml --run-name baseline_burgers_seed42
python evaluate.py --config configs/base.yaml --ckpt runs/baseline_burgers_seed42/checkpoint.json
python tools/summarize.py --runs-dir runs --out results/raw/summary.csv
```


## Visualization module (新增)

参考常见 PINN/TSK 开源仓库的实验展示方式（训练曲线 + 消融柱状图），新增：

- `tools/visualize.py`
  - 读取 `runs/*/history.csv` 生成 `results/figures/loss_curves.svg`
  - 读取 `results/raw/summary.csv` 生成 `results/figures/ablation_l2.svg`

```bash
python tools/visualize.py --run-dir runs --summary-csv results/raw/summary.csv --out-dir results/figures --run-name baseline_burgers_seed42
```

## Ablation examples

```bash
python train.py --config configs/ablation/no_conflict_weight.yaml --run-name ablation_no_conflict_weight
python train.py --config configs/ablation/no_rule_balance.yaml --run-name ablation_no_rule_balance
```
