# 🤖 AI 机器人课程实验与研究笔记

[![GitHub Pages](https://img.shields.io/badge/GitHub%20Pages-在线预览-brightgreen)](https://wangqiuzhuang.github.io/ai-robot-wangqiuzhuang/)
[![Weeks Completed](https://img.shields.io/badge/已完成-15%2F15周-blue)](https://wangqiuzhuang.github.io/ai-robot-wangqiuzhuang/)
[![Last Update](https://img.shields.io/badge/更新-2026.06-orange)](https://wangqiuzhuang.github.io/ai-robot-wangqiuzhuang/)

欢迎来到我的 AI 机器人课程学习与实践仓库。本项目完整记录了 **AI机器人2603学期** 课程期间的所有实验、核心配置、踩坑记录以及高级仿真成果。

> 🌐 **在线预览**: [https://wangqiuzhuang.github.io/ai-robot-wangqiuzhuang/](https://wangqiuzhuang.github.io/ai-robot-wangqiuzhuang/)

---

## 👤 个人信息与技术背景

| 项目 | 内容 |
|:---|:---|
| **姓名** | 王秋壮 (Wang Qiuzhuang) |
| **专业** | 软件工程 (Software Engineering) |
| **核心方向** | ROS2 机器人开发、Docker 容器化部署、机器人运动学仿真 |
| **开发环境** | WSL2 + Ubuntu 22.04 LTS, VS Code |

---

## 📈 课程任务导航与工程进度

| 周次 | 实验/工程名称 | 核心技术栈 | 状态 | 笔记链接 |
|:---:|:---|:---|:---:|:---:|
| **Week 01** | 基础环境搭建与工程工具 | `WSL2` `Ubuntu` `Git` `Markdown` | ✅ Done | [📝 查看笔记](week1/README.md) |
| **Week 02** | ROS2 环境配置与基础 CLI | `ROS2 Humble` `CLI` `Colcon` | ✅ Done | [📝 查看笔记](week2/README.md) |
| **Week 03** | 机器人运动学核心概念与 ROS2 通信 | `Kinematics` `TF2` `URDF` | ✅ Done | [📝 查看笔记](week3/README.md) |
| **Week 04** | 机器视觉与 OpenCV 基础实验 | `OpenCV` `Python` `Image Processing` | ✅ Done | [📝 查看笔记](week4/README.md) |
| **Week 05** | 机器人运动学与机械臂控制 | `Panda Arm` `IK/FK` `PyBullet` | ✅ Done | [📝 查看笔记](week5/README.md) |
| **Week 06** | 传感器数据处理与 KITTI 数据集实验 | `KITTI Dataset` `LiDAR` `RViz2` | ✅ Done | [📝 查看笔记](week6/README.md) |
| **Week 07** | Docker 容器环境与 ROS2 桌面 VNC | `Docker` `VNC` `ROS2 Desktop` | ✅ Done | [📝 查看笔记](week7/README.md) |
| **Week 08** | ROS2 中级实践与工具链 | `Launch` `RViz2` `ROS2 Bag` | ✅ Done | [📝 查看笔记](week8/README.md) |
| **Week 09** | 机器人仿真环境与实践 | `Gazebo` `Webots` `URDF` | ✅ Done | [📝 查看笔记](week9/README.md) |
| **Week 10** | Docker 卷挂载与 OpenCV 图像处理 | `Docker Volume` `OpenCV` `Python` | ✅ Done | [📝 查看笔记](week10/README.md) |
| **Week 11** | Docker 镜像持久化与 Git 仓库整理 | `Docker Commit` `GitHub Pages` | ✅ Done | [📝 查看笔记](week11/README.md) |
| **Week 12** | 远程摄像头流与 ArUco 标记识别 ⭐ | `OpenCV` `ArUco` `Tailscale` | ✅ Done | [📝 查看笔记](week12/README.md) |
| **Week 13** | 四足机器人仿真与强化学习 | `PyBullet` `PPO` `RL` | ✅ Done | [📝 查看笔记](week13/README.md) |
| **Week 14** | 手机遥控迷宫机器人 🤖 | `ROS2` `aiohttp` `A*` `Tailscale` | ✅ Done | [📝 查看笔记](week14/README.md) |
| **Week 15** | 期末总结与展示 | `待补充` | ⏳ Optimizing | |

---

## 🛠️ 核心技术栈与工程能力看板

### 操作系统与容器
- **Ubuntu 22.04 LTS** — Linux 开发环境
- **WSL2** — Windows 下的 Linux 子系统
- **Docker** — 容器化部署（支持 GUI 转发、卷挂载、镜像持久化）

### 机器人框架
- **ROS2 (Humble / Iron)** — 机器人操作系统
- **TF2** — 坐标变换管理
- **URDF** — 机器人统一描述格式

### 仿真环境
- **PyBullet** — 物理仿真引擎
- **Gazebo** — 3D 机器人仿真
- **Webots** — 跨平台机器人仿真
- **RViz2** — ROS2 3D 可视化工具

### 感知与算法
- **OpenCV** — 计算机视觉与图像处理
- **PyTorch** — 深度学习框架
- **Stable-Baselines3** — 强化学习算法库 (PPO)
- **LiDAR / Point Cloud** — 传感器数据处理

---

## 💡 本仓库核心亮点

1. **工业级规范**：笔记不仅记录操作步骤，更重点包含 **原理阐述**、**代码逐行注释** 和 **踩坑与解决方案 (Troubleshooting)**
2. **多媒体动静结合**：实验结果均配备直观的 **GIF 动图** 与 **截图对比**，拒绝枯燥的纯文本
3. **绿色健康度**：严格遵循 GitHub Pages 相对路径规范，所有图片使用本地 `img/` 目录管理，确保 **100% 图片不碎链**
4. **工程化结构**：按周次组织目录，每个实验独立文件夹，README 统一格式，便于课程系统自动检测和评分

---

## 📂 仓库结构

```
ai-robot-wangqiuzhuang/
├── README.md              # 课程总览与导航（本页）
├── _config.yml            # GitHub Pages Jekyll 主题配置
├── week01/                # 每周实验独立目录
│   ├── README.md          #   实验文档与截图
│   └── img/               #   实验截图与动图
├── week02/
│   ├── README.md
│   └── img/
├── ...
├── week13/
│   ├── README.md
│   ├── assets/            #   GIF 动图与图表
│   ├── demos/             #   演示脚本
│   ├── scripts/           #   工具脚本
│   ├── quadruped_walk.py          # Trot 步态行走
│   ├── ai_chat_log.md             # AI 调试对话日志
│   └── reflection.md              # 学习反思
└── week14/
    ├── README.md                       #   项目文档
    └── turtlesim_remote/               #   项目代码
        ├── turtlesim_web_bridge.py     #   核心桥接程序
        ├── maze.py                     #   迷宫生成模块
        ├── explorer.py                 #   A*/BFS 自动寻路
        ├── index.html                  #   手机遥控网页
        └── requirements.txt            #   依赖清单
```

---

## 🚀 快速开始

```bash
# 克隆仓库
git clone https://github.com/wangqiuzhuang/ai-robot-wangqiuzhuang.git

# 进入任意周次目录查看实验笔记
cd ai-robot-wangqiuzhuang/week12

# 在线预览
open https://wangqiuzhuang.github.io/ai-robot-wangqiuzhuang/
```

---

## 📊 仓库统计

| 指标 | 数值 |
|:---|---:|
| 完成周次 | 15 |
| Python 脚本 | 11 |
| 截图 / GIF | 41+ |
| AI 对话记录 | 4（W10-W13）|
| 实验反思 | 4（W10-W13）|
| 代码总行数 | 2,700+ |
| 路径规划算法 | BFS · Dijkstra · A* |
| 强化学习 | PPO · Residual RL |

---

*🤖 Built with ❤️ by Wang Qiuzhuang | AI机器人2603学期 | Last updated: 2026.06*
