# Week 13: AI 辅助调试对话日志 — 四足机器人步态优化

> 以下记录了使用 AI (DeepSeek/Claude) 辅助调试四足机器人步态的 5+ 轮对话

---

## 对话 1: PyBullet 环境加载问题

**我**: 我运行 `python3 demos/02_load_laikago.py` 时遇到错误: `ImportError: No module named 'pybullet'`，怎么解决？

**AI**: 这是因为你的 Python 环境中没有安装 PyBullet。执行:
```bash
pip3 install pybullet
```
如果使用 Docker 容器，需要先进入容器终端再安装。安装完成后可以用 `python3 -c "import pybullet; print(pybullet.__version__)"` 验证。

**我**: 谢谢！安装成功后 Laikago 机器狗正常加载了。但我发现机器狗悬空在地面上方，没有落到地面。这是什么原因？

**AI**: 这是 PyBullet 的正常行为——URDF 模型的初始位置由 `basePosition` 参数决定。如果你设置的高度太高（如 z=0.5），需要等待几个仿真步长让重力把机器人拉下来。在仿真循环中添加 `time.sleep(1.0)` 让物理引擎有时间处理重力。或者把 basePosition 的 z 坐标设置为模型自身高度（Laikago 约 0.25m）。

---

## 对话 2: 步态生成与关节控制

**我**: 我想让四足机器人走 Trot 步态。Trot 步态的对角腿相位关系是怎样的？

**AI**: Trot（对角小跑）步态是四足机器人最常用的步态之一。四条腿分为两组:
- **组 A**: 左前腿 (LF) + 右后腿 (RH) — 同时抬起/落地
- **组 B**: 右前腿 (RF) + 左后腿 (LH) — 同时抬起/落地
- **相位差**: 两组之间相差 π (180°)，即一组落地时另一组抬起

控制代码的关键:
```python
phase_A = 2 * math.pi * frequency * time
phase_B = phase_A + math.pi  # 180° 相位差

for leg in group_A:
    joint_angle = amplitude * math.sin(phase_A)
for leg in group_B:
    joint_angle = amplitude * math.sin(phase_B)
```

占空比 (duty cycle) 设为 0.5 表示每条腿 50% 时间着地。

**我**: 我按你说的实现了，但机器狗在原地踏步不前进。哪里出错了？

**AI**: 原地踏步说明只有上下运动，缺少前进方向的分量。检查:
1. **髋关节 (hip) 是否有前后摆动** — Trot 步态中髋关节也需要正弦运动来产生前进推力
2. **膝关节和髋关节的相位关系** — 通常膝关节比髋关节滞后 π/2
3. **幅值是否足够** — hip 振幅建议 0.3-0.5 rad，knee 振幅 0.5-0.8 rad

---

## 对话 3: 奖励函数调优

**我**: 我在用 PPO 训练四足机器人爬楼梯。当前的奖励函数是 `reward = forward_velocity - energy_penalty`，但机器人学会的是原地踏步而不是爬楼梯。怎么改进？

**AI**: 你的奖励函数缺少对"向上运动"的激励。建议添加高度奖励:

```python
# 改进的奖励函数
forward_reward = base_velocity_x * dt          # 前进奖励
height_reward = (current_height - prev_height) * 10.0  # 高度变化奖励
energy_penalty = sum(torque**2) * 0.001       # 能耗惩罚
survival_bonus = 0.5                           # 存活奖励
stair_progress = (current_x - start_x) * 2.0  # 楼梯进度奖励

total_reward = (
    forward_reward * 1.0 +
    height_reward * 5.0 +      # 加重高度奖励
    stair_progress * 2.0 +     # 楼梯进度
    survival_bonus -
    energy_penalty
)
```

关键调整:
1. **height_reward 权重加大** — 鼓励机器人抬腿
2. **提前终止惩罚** — 如果机器人躺倒 (roll/pitch > 阈值)，给予负奖励并结束 episode
3. **课程学习** — 从平地开始训练，逐步增加台阶高度

**我**: 加了高度奖励后，机器人开始尝试抬腿了，但训练到后期奖励曲线震荡很厉害。怎么稳定训练？

**AI**: 震荡通常是因为学习率过高或 entropy coefficient 不匹配。尝试:
1. **降低学习率** 从 3e-4 到 1e-4
2. **增大 batch size** 从 64 到 256
3. **调整 entropy_coef** 从 0.01 降到 0.005（后期需要更多 exploitation）
4. **增加 n_steps** 从 2048 到 4096，收集更多样本再更新

---

## 对话 4: 台阶高度泛化问题

**我**: 机器人在 0.03m 台阶上训练好了，但换到 0.05m 台阶就完全不行。怎么提高泛化能力？

**AI**: 这是典型的过拟合问题。解决方法 — **Domain Randomization**:

```python
# 每个 episode 随机化台阶参数
step_height = np.random.uniform(0.02, 0.06)   # 随机高度
step_width = np.random.uniform(0.15, 0.25)     # 随机宽度
num_steps = np.random.randint(3, 6)            # 随机台阶数
friction = np.random.uniform(0.5, 1.5)         # 随机摩擦系数
```

同时建议:
- 在 `vec_env` 中使用多个并行环境，每个环境配置不同台阶参数
- 观测中加入台阶高度信息 (privileged information)
- 训练步数增加到 5M+ 步以充分探索参数空间

---

## 对话 5: 最终效果评估

**我**: 训练了 3M 步后，机器人能爬上 3 级 0.03m 的台阶了。但离"在最高台阶上稳定站住"还有差距。下一步优化方向?

**AI**: 恭喜取得阶段性成果！从"能爬上去"到"站稳"需要:

1. **添加静止奖励** — 到达目标区域后，奖励保持零速度的姿态控制
2. **末端奖励** — 到达目标台阶顶部时给予大的成功奖励 (+10)
3. **增加平衡训练** — 在台阶顶部随机施加小的外力扰动，训练抗干扰能力
4. **分层策略** — Stage 1: 学会走路 → Stage 2: 学会爬楼梯 → Stage 3: 学会在顶部停止

建议先增加末端奖励，这通常效果最明显。

**我**: 谢谢！我会试试添加末端奖励和平衡训练。另一个问题：视频中机器人爬楼梯的动作看起来很不自然，像"跳"上去的而不是"走"上去的。怎么让步态更自然？

**AI**: 步态不自然通常是因为:
1. **动作平滑度** — 在奖励中加入 `action_smoothness_penalty`: `-0.01 * sum((action_t - action_{t-1})**2)`
2. **关节限位约束** — 确保输出动作被 clip 在关节合理范围内
3. **参考轨迹引导** — 加入模仿学习损失，让策略输出的关节角度接近手工设计的 Trot 步态参考轨迹
4. **降低 action noise** — PPO 训练后期的 exploration noise 应该衰减

---

## 对话 6: 代码整合与提交

**我**: 我的 `quadruped_walk.py` 整合了 Trot 步态和 PPO 控制器，需要整理提交。有什么建议？

**AI**: 建议提交结构:
```
week13/
├── quadruped_walk.py          # 主程序 (Trot + PPO)
├── ai_chat_log.md             # 本对话日志
├── reflection.md              # 学习反思
├── demos/                     # 演示代码
│   ├── 01_pybullet_box.py
│   ├── 02_load_laikago.py
│   ├── 03_sine_gait.py
│   └── 04_trot_gait.py
├── scripts/                   # 辅助脚本
├── assets/                    # GIF 和图片
└── README.md                  # 实验报告
```

确保:
- README 包含运行命令和预期结果
- 对话日志记录真实的调试过程
- reflection.md 覆盖 3 个反思问题

---

> 📝 以上对话基于实际调试过程记录，展示了如何使用 AI 工具辅助四足机器人步态开发和强化学习训练。
