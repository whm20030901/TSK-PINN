# Paper Alignment Checklist (HD_TSK_PINN_v3_Final)

## 当前实现状态说明

目前完成的是 **实验编排与复现骨架**，不是完整数值求解器。
核心目标是：先把论文 4.x/5.x/6.x 的模块与实验流程映射到可执行程序入口和统一配置，再逐步替换为真实 PINN/TSK 训练实现。

## 论文-代码对齐表

| Paper Section | 对应实现 | 当前状态 | 备注 |
|---|---|---|---|
| 4.1 Hierarchical TSK Antecedent | `configs/* -> modules.hierarchical_antecedent` | scaffold-ready | 已可做开关消融 |
| 4.2 Shared-Backbone Adapter Consequents | `configs/* -> modules.adapter_consequent` | scaffold-ready | 已可做开关消融 |
| 4.3 Difficulty Scoring + Rule Evolution | `configs/* -> modules.difficulty_score` | scaffold-ready | 已可做开关消融 |
| 4.4 Rule-Balance Regularization | `configs/* -> modules.rule_balance_reg` | scaffold-ready | 已可做开关消融 |
| 4.5 Conflict-Aware Task Weighting | `configs/* -> modules.conflict_aware_weighting` | scaffold-ready | 已可做开关消融 |
| 5.1 Initialization | `configs/base.yaml` 初始化参数入口 | scaffold-ready | 可继续细化初始化策略 |
| 5.2 Computational Cost Analysis | `checkpoint.json` 中参数量与单epoch耗时字段 | scaffold-ready | 可替换成真实 profiler |
| 5 Training Algorithm | `train.py`（训练主入口） | scaffold-ready | 可替换为真实 PINN 反向传播 |
| 6.1 Implementation | `README.md` + CLI 流程 | scaffold-ready | 复现实验入口已统一 |
| 6.2 Baselines | `configs/pde/*.yaml` + `experiment_registry.yaml` | scaffold-ready | 可扩展更多 baseline |
| 6.3 Results | `evaluate.py` 输出 `evaluation.csv` | scaffold-ready | 指标输出已标准化 |
| 6.4 Ablation Studies | `configs/ablation/*.yaml` | scaffold-ready | 模块级消融已支持 |
| 6.5 Analysis per PDE | `tools/summarize.py` 汇总跨运行结果 | scaffold-ready | 可加统计检验/绘图 |

## 新增文档说明（本次补充）

- 在 `README.md` 新增“我现在已经完成了什么（对应论文）”章节。
- 明确声明当前进度是“可执行实验骨架”。
- 明确每一项功能对应到论文 4.x/5.x/6.x 的具体位置。
