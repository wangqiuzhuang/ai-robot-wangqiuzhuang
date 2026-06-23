# Week 14: 手机遥控迷宫机器人 🤖📱

> 🏆 **期末小组项目** — 方向 B (turtlesim 2D 迷宫)

## 本周概览

使用手机浏览器通过 Tailscale 组网发送控制命令到 WSL 中的 ROS2 turtlesim，实现小乌龟在迷宫中的手动遥控和 A*/BFS 自动探索。

## 项目架构

```
手机浏览器 (index.html)
    ↕ WebSocket (Tailscale)
turtlesim_web_bridge.py (单一常驻程序)
    ├── aiohttp WebSocket 服务器
    ├── ROS2 Node (发布 /turtle1/cmd_vel，订阅 /turtle1/pose)
    ├── 碰撞检测 (迷宫边界 + 障碍物)
    └── explorer.py (A*/BFS 自动探索)
            ↓
        turtlesim_node (ROS2)
```

## 文件结构

| 文件 | 说明 |
|:---|:---|
| `turtlesim_web_bridge.py` | 核心桥接程序：WebSocket + ROS2 节点 + 碰撞检测 + 自动模式 |
| `maze.py` | 迷宫生成模块：5×5 网格 + 递归回溯 + 编织环路 |
| `explorer.py` | A* + BFS 双重寻路算法 + 性能对比 |
| `index.html` | 手机遥控网页：方向键 + 自动/手动切换 + Canvas 路径可视化 |
| `requirements.txt` | Python 依赖 (aiohttp) |

## 功能特性

### 手动遥控
- 🕹️ 方向键长按控制（前进/后退/左转/右转）
- 🛑 松开自动停止
- 🧱 内置碰撞检测（碰到障碍物或边界自动拦截）
- 🏁 到达终点自动停止

### 自动探索
- 🤖 一键启动 A* 自动寻路
- 🗺️ Canvas 实时显示规划路径 (waypoints)
- 🔄 碰撞后自动重新规划
- 📊 BFS vs A* 性能对比 (explorer.py 自测)

## 运行方式

```bash
# 1. 安装依赖
pip install aiohttp

# 2. 终端1: 启动 turtlesim
source /opt/ros/humble/setup.bash
ros2 run turtlesim turtlesim_node

# 3. 终端2: 启动桥接程序
source /opt/ros/humble/setup.bash
cd week14
python3 turtlesim_web_bridge.py

# 4. 手机浏览器访问 (同一 Tailscale 网络)
# http://<WSL的Tailscale_IP>:8080
```

## 算法验证

```bash
# 验证迷宫可解性
python3 maze.py

# 对比 BFS 和 A* 性能
python3 explorer.py
```

## 踩坑记录

| 问题 | 原因 | 解决方案 |
|:---|:---|:---|
| 手机打不开页面 | Tailscale IP 不对 | `tailscale ip -4` 确认 WSL 地址 |
| 连接断开 | 桥接程序挂了 | 保持终端运行，不要关闭 |
| 乌龟不停 | touchend 未触发 | 检查手机浏览器 touch 事件支持 |
| turtlesim 不动 | 未 source ROS2 | 每个终端都要 source setup.bash |

---

## 总结

本项目按照课程 Week 14 方向 B 要求，完成了：单一常驻桥接程序、手机网页遥控、迷宫碰撞检测、A* 自动探索。代码基于课程 starter 修改，核心改动为桥接程序集成 explorer 自动模式和网页增加自动/手动切换按钮。
