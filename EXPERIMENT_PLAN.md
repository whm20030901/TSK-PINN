# 基于《HD_TSK_PINN_v3_Final》 的实验执行计划（对齐论文结构）

> 说明：本计划严格按仓库内 PDF 的章节推进，核心围绕 **4. HD-TSK-PINN: Architecture and Formulation**、**5. Training Algorithm**、**6. Experiments** 展开。

## 0. 先做论文对齐清单（必须完成）

根据 PDF 目录可确认本工作主线包括：
- 4.1 Hierarchical TSK Antecedent（含 Coarse/Fine 规则）
- 4.2 Shared-Backbone Adapter Consequents（含参数量分析）
- 4.3 Region-Level Difficulty Scoring and Rule Evolution
- 4.4 Rule-Balance Regularization
- 4.5 Gradient-Conflict-Aware Task Weighting
- 5.1 Initialization, 5.2 Computational Cost, 5 Training Algorithm
- 6.1 Implementation, 6.2 Baselines, 6.3 Results, 6.4 Ablation, 6.5 Analysis per PDE

**交付物**：`docs/paper_alignment_checklist.md`
- 把论文每个子模块映射到代码模块（文件路径、函数名、开关配置）。
- 每个模块标注状态：`implemented / missing / differs`。

---

## 1. 建立“可复现骨架”（先不做大规模优化）

### 1.1 固化实验配置
- 建立统一配置：
  - `configs/base.yaml`
  - `configs/pde/*.yaml`（按不同 PDE）
  - `configs/ablation/*.yaml`（按模块开关）
- 配置项必须覆盖：
  - PDE 定义、采样数量、网络宽深、规则数（coarse/fine）、loss 任务项、优化器、seed。

### 1.2 固化运行入口
- 训练入口：`python train.py --config ...`
- 评估入口：`python evaluate.py --config ... --ckpt ...`
- 汇总入口：`python tools/summarize.py --runs_dir ...`

### 1.3 固化日志与版本信息
每次 run 自动记录：
- git commit hash
- 配置 hash
- 随机种子
- 设备与耗时
- 指标（L2 error、PDE residual、BC/IC error）

**交付物**：`experiment_registry.yaml` + `results/raw/*.csv`

---

## 2. 按 4.x 模块逐项复现实验（核心阶段）

> 原则：一次只引入一个模块，先验证“是否有效”，再做组合。

### 2.1 复现 4.1：Hierarchical TSK Antecedent
- 从单层规则开始，再切换到 coarse→fine 层次规则。
- 扫描 `K_coarse`、`K_fine` 组合：如 (2,4), (4,8), (8,16)。
- 记录规则激活分布，检查是否出现“少数规则垄断”。

### 2.2 复现 4.2：Shared-Backbone Adapter Consequents
- 对比两种 consequent：
  1) 完全独立专家头
  2) shared backbone + adapter
- 对齐论文中的参数量与性能权衡：
  - 参数总量
  - 单步训练耗时
  - 最终误差

### 2.3 复现 4.3：Region-Level Difficulty + Rule Evolution
- 实现 neighborhood-smoothed residual（避免只看点残差）。
- 形成规则级 difficulty 分数 `D_ab`。
- 验证 `D_ab` 的三类用途（论文 4.3.4）：
  - 采样重分配
  - 规则演化/增减
  - 训练权重调节

### 2.4 复现 4.4：Rule-Balance Regularization
- 增加规则均衡正则，抑制模式塌缩。
- 关键观察：
  - 各规则使用熵是否上升
  - 误差是否稳定下降

### 2.5 复现 4.5：Gradient-Conflict-Aware Task Weighting
- 周期性估计任务梯度冲突（EMA 平滑）。
- 联合 difficulty + conflict 计算任务权重。
- 对比静态权重与常见自适应权重（如 GradNorm 类方法）。

**交付物**：`results/module_repro/*.csv` + `results/figures/module_*.png`

---

## 3. 按 5.x 训练算法落地（初始化 + 计算成本 + 调度）

### 3.1 复现 5.1 Initialization
- 严格按论文初始化流程：
  - 主干网络初始化
  - 规则参数初始化
  - 若有阶段式 warmup，单独开关可控

### 3.2 复现 5.2 Computational Cost Analysis
- 实测而非只估计：
  - 参数量
  - FLOPs（可选）
  - 每 epoch 时间
  - 峰值显存
- 输出与 baseline 对照表。

### 3.3 训练调度
- 默认两阶段优化：Adam 预训练 + L-BFGS 精调（如论文设置包含该策略）。
- 记录每阶段贡献（误差下降分解）。

**交付物**：`results/cost_report.md` + `results/cost_table.csv`

---

## 4. 按 6.x 组织正式实验（Implementation / Baselines / Results / Ablation / PDE分析）

### 4.1 6.1 Implementation 对齐
- 明确硬件、框架版本、batch 与采样策略。
- 写入 `docs/repro_env.md`。

### 4.2 6.2 Baselines
最少三组：
1. 标准 PINN
2. 你当前实现（去掉 HD 模块）
3. HD-TSK-PINN 完整版

### 4.3 6.3 Results
- 每个 PDE 输出：均值±标准差（3~5 seeds）。
- 输出收敛曲线 + 最终误差表。

### 4.4 6.4 Ablation
按论文模块拆解消融：
- `-hierarchical antecedent`
- `-adapter consequent`
- `-difficulty score`
- `-rule-balance reg`
- `-conflict-aware weighting`

### 4.5 6.5 Analysis per PDE
- 每个 PDE 单独写“哪一模块贡献最大”的分析段。
- 给出失败案例（如高频区域、边界尖峰）和可视化。

**交付物**：`results/report.md`（可直接用于论文/汇报）

---

## 5. 多智能体（Codex）执行编排方案

为避免“计划写得好但执行混乱”，建议 5 个 agent：

1. **Orchestrator Agent**：生成任务 DAG，维护 `experiment_registry.yaml`
2. **Paper-Alignment Agent**：专门核对论文 4.x/5.x/6.x 到代码映射
3. **Implementation Agent**：按模块最小侵入实现 + 测试
4. **Runner Agent**：批量跑 seeds 与 ablation
5. **Analysis Agent**：自动出图与结论

执行顺序：
- `Paper-Alignment -> Implementation -> Runner -> Analysis -> Orchestrator复盘`

---

## 6. Skills 与 MCP 的具体使用（只做“增益项”）

### 6.1 Skills（建议新增）
- `hd-tsk-module-repro-skill`：按 4.1~4.5 自动生成消融任务。
- `pde-benchmark-runner-skill`：按 PDE 模板批量运行并汇总。
- `repro-audit-skill`：检查 seed/依赖/日志完备性。

### 6.2 MCP
- GitHub MCP：检索 PINN/TSK 开源实现的可迁移训练细节。
- Artifact MCP：读取既往结果，避免重复实验。

### 6.3 约束
- 任何外部策略必须记录来源、commit、迁移理由。
- 不直接复制外部实现；先做小规模验证再集成。

---

## 7. 一周落地排期（可直接执行）

### Day 1
- 完成 paper-alignment checklist
- 跑通 baseline（1个 PDE，1个 seed）

### Day 2-3
- 复现 4.1 + 4.2，并提交阶段报告

### Day 4
- 复现 4.3 + 4.4

### Day 5
- 复现 4.5，完成主要 ablation

### Day 6
- 多 seed 正式实验 + 成本分析（5.2）

### Day 7
- 形成 `results/report.md` 与推荐默认配置

---

## 8. 验收标准（DoD）

满足以下条件才算“实验完成”：
1. 论文 4.x/5.x/6.x 各模块均有代码映射与结果证据。
2. 所有核心表格可由脚本一键重现。
3. 至少 1 个 PDE 达到优于标准 PINN 的稳定提升（多 seed）。
4. 有失败案例与局限性说明（对应论文 Discussion 思路）。

> 如果你愿意，下一步我可以直接给出 `experiment_registry.yaml` 与 `configs/base.yaml` 的首版模板，按这个计划当天就能开跑。


## 当前进展记录（自动化进入下一阶段）

- 当前阶段：**Stage 4 - Paper-aligned ablation with statistical support**。
- 已执行批量实验：3 个变体（`baseline_burgers`、`no_conflict_weight`、`no_rule_balance`）× 3 seeds（42/43/44），共 9 组运行。
- 当前结果（L2 mean）：
  - `baseline_burgers`: 0.075707
  - `no_rule_balance`: 0.080096
  - `no_conflict_weight`: 0.081193
- 阶段结论：在当前实验设置下，完整 baseline 优于两个消融变体，说明 `rule_balance` 与 `conflict_weighting` 两个模块对指标有正向贡献。
- 下一步（进入论文 6.5 分析阶段）：
  1. 增加 PDE 任务（至少加入 heat_1d 对照）；
  2. 增加更多消融维度（如 hierarchical_antecedent / adapter_consequent）；
  3. 将当前模拟后端替换为真实 PINN 优化，以形成可发表结论。
