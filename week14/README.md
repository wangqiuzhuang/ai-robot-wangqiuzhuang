# Week 14: 综合项目实战 — turtlesim 迷宫自动探索

> 🎯 **期末综合项目** — 手机 Web 遥控 + 路径规划算法自动走出迷宫

## 项目概述

本项目实现了一个完整的迷宫探索系统，包含三大模块：

- **Web 遥控器**：手机浏览器作为控制器，通过 Tailscale 虚拟组网连接到 WSL
- **桥接程序**：WebSocket ↔ ROS2 的双向通信桥梁，包含碰撞检测和安全保护
- **路径规划**：BFS / Dijkstra / A* 三种算法实现自动探索，可运行时切换对比

## 系统架构

```
📱 手机浏览器 (HTTPS 页面)
    │ 触摸事件 (方向键 / 自动探索按钮)
    │ WebSocket JSON 指令
    ▼
🐍 Python 桥接程序 (turtlesim_web_bridge.py)
    │ ROS2 /turtle1/cmd_vel 话题
    ▼
🐢 turtlesim 乌龟 (ROS2 仿真)
    │ /turtle1/pose 话题
    ▼
📊 状态回传 (WebSocket → 网页显示遥测 + 迷宫预览)
```

## 文件说明

| 文件 | 说明 |
|------|------|
| `turtlesim_web_bridge.py` | 主控程序：WebSocket 服务 + ROS2 桥接 + 自动/手动模式切换 |
| `explorer.py` | 路径规划模块：BFS、Dijkstra、A* 三种算法实现 + 统计对比 |
| `maze.py` | 迷宫生成：递归回溯 + 编织(Braid) + BFS 自校验 |
| `index.html` | 手机遥控器网页：方向键 + 自动探索按钮 + 算法选择器 + 迷宫预览 |

## 运行方式

### 1. 环境要求

- Docker 容器内已安装 ROS2 (Humble) + turtlesim
- Tailscale 已在 WSL 和手机上登录同一账号
- Python 依赖：`aiohttp`, `geometry_msgs`, `turtlesim`

```bash
pip install -r requirements.txt
```

### 2. 启动 turtlesim

在 Docker 容器的终端中：

```bash
ros2 run turtlesim turtlesim_node
```

### 3. 启动桥接程序

```bash
cd week14
python turtlesim_web_bridge.py
```

控制台输出：`Turtlesim starter listening on http://0.0.0.0:8080`

### 4. 手机访问

手机浏览器打开 `http://<wsl-tailscale-ip>:8080`（IP 地址在 Tailscale 控制台查看）

## 功能说明

### 手动遥控模式（默认）

- 长按 ↑↓←→ 控制乌龟移动，松开自动停止
- ■ 按钮紧急停止
- ↺ 按钮重置乌龟到起点

### 自动探索模式

- 点击「🤖 自动探索」按钮，路径规划算法接管控制
- 支持三种算法切换：
  - **BFS**：广度优先，保证最短路径，扩展节点最多
  - **Dijkstra**：考虑安全代价（靠墙走代价更高），路径更安全
  - **A\***：曼哈顿启发式，收敛最快，扩展节点最少（默认）
- 算法切换实时生效，下次规划使用新算法
- 到达终点后自动停止，显示 🏁

### 迷宫预览

Canvas 实时绘制迷宫地图，显示：
- 灰色墙壁（递归回溯 + 编织环路）
- 绿色起点 / 金色终点
- 蓝色乌龟（碰撞时变红，到达终点变绿）
- 乌龟朝向指示线

### 遥测面板

实时显示：位置坐标、朝向角、当前指令、实际执行指令、碰撞状态

## 实验过程截图

### 1. 启动 turtlesim 节点

![启动turtlesim](img/start-turtlesim.png)

### 2. 手机连接遥控器页面

![手机遥控器](img/phone-controller.png)

### 3. 手动遥控乌龟走迷宫

![手动遥控](img/manual-control.png)

### 4. 自动探索模式（A* 路径规划）

![自动探索](img/auto-explore.png)

### 5. 到达终点

![到达终点](img/goal-reached.png)

### 6. 算法对比统计

![算法对比](img/algo-comparison.png)

## 算法对比结果

| 算法 | 扩展节点数 | 路径长度 | 特点 |
|------|:---:|:---:|------|
| BFS | 最多 (~20) | 最短 | 无权图最优，无启发信息 |
| Dijkstra | 中等 (~15) | 稍长 | 考虑安全代价，路径更保守 |
| A* | 最少 (~8) | 最短 | 曼哈顿启发，效率最高 |

## 踩坑记录

| 问题 | 原因 | 解决方案 |
|------|------|------|
| 手机浏览器无法调用摄像头（仅体验控制不需要） | 仅遥控不需要摄像头权限 | 本项目不涉及摄像头，纯 WebSocket 控制 |
| Tailscale IP 变化后手机连不上 | WSL 重启后 Tailscale 重新分配 IP | 每次启动后在 Tailscale 控制台确认当前 IP |
| 自动模式乌龟原地打转 | 朝向角误差判断阈值太大 | 调整 `TURN_FIRST` 从 0.8 降到 0.6 |
| Dijkstra 规划路径绕远路 | 代价函数边缘惩罚太重 | 把边缘格代价从 2.0 降到 1.5 |
| 网页按钮在手机上太小 | 初始按钮高度 52px 不够 | 改为 `min-height: 68px`，适配手指触控 |

## 总结

本周综合项目成功实现了「手机 Web 遥控器 → Tailscale 组网 → WebSocket 通信 → ROS2 turtlesim 控制」的完整数据链路，并集成了 BFS / Dijkstra / A* 三种路径规划算法实现迷宫自动探索。

这个项目串联了本学期多个技术栈：
- **Week 5-7**：Docker 容器环境 → 本次的 ROS2 runtime
- **Week 9**：路径搜索算法 → explorer.py 的 A* 实现
- **Week 10-11**：GitHub Pages 部署 → 最终展示
- **Week 12**：Tailscale + WebSocket 通信 → 手机遥控链路

作为 1 人组完成方向 B（turtlesim 迷宫），本项目实现了所有必需功能（遥控、碰撞保护、自动探索）并增加了算法对比统计作为进阶特性。
