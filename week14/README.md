# Week 14: 手机遥控迷宫机器人 🤖📱

> 🏆 **期末小组项目** — 方向 B (turtlesim 迷宫探索变体)

## 本周概览

本项目实现了一个完整的手机遥控迷宫机器人系统，打通了「手机浏览器 → WebSocket → Python 后端 → 迷宫生成 → 自动寻路」的完整链路。

## 文件结构

```
week14/
├── README.md                # 本文件
├── img/                     # 截图与演示素材
└── maze_app/                # 项目代码
    ├── index.html           # 手机遥控网页 (Canvas + D-Pad)
    ├── server.py            # Tornado WebSocket 桥接服务器
    ├── maze.py              # 递归回溯迷宫生成
    ├── explorer.py          # BFS / A* 自动寻路
    └── week14_report.md     # 项目报告
```

## 技术架构

| 层级 | 技术 | 说明 |
|:---|:---|:---|
| 📱 前端 | HTML5 Canvas + WebSocket | 手机浏览器触摸遥控，迷宫实时渲染 |
| 🌐 通信 | Tornado WebSocket | JSON 双向实时通信，多客户端并发 |
| 🧩 算法 | BFS + A* | 最短路径搜索与自动探索 |
| 🗺️ 迷宫 | 递归回溯算法 | 完美迷宫生成（全连通、唯一解）|

## 功能特性

### 手机遥控 (index.html)
- 🕹️ D-Pad 方向键：触摸控制上下左右移动
- 🎨 Canvas 实时渲染：迷宫墙壁、路径、机器人位置
- 📊 状态面板：坐标、步数、探索进度
- 📱 移动端优化：防双击缩放、触摸事件处理

### 迷宫生成 (maze.py)
- 递归回溯算法保证完美迷宫
- Cell 数据结构维护 N/S/E/W 四面墙壁
- `to_dict()` 序列化接口供前端渲染
- `to_ascii()` 终端调试输出

### 寻路算法 (explorer.py)
- BFS 广度优先搜索 — 保证最短路径 O(V+E)
- A* 启发式搜索 — 曼哈顿距离启发函数
- 自动探索器 — 增量探索 + 兴趣点记录
- `benchmark()` BFS vs A* 性能对比

### 后端服务 (server.py)
- Tornado 异步框架，多客户端并发
- WebSocket 实时推送路径动画
- 支持手动/自动 BFS/自动 A*/自动探索四种模式

## 运行方式

```bash
pip install tornado
cd week14/maze_app

# 启动服务器
python3 server.py

# 手机浏览器访问 (确保同一网络)
# http://<电脑IP>:5000

# 本地测试
# http://localhost:5000

# 验证模块
python3 maze.py          # 终端输出 ASCII 迷宫
python3 explorer.py      # BFS vs A* 性能对比
```

## 算法对比

| 指标 | BFS | A* |
|:---|:---|:---|
| 时间复杂度 | O(V+E) | O(E) 最坏 |
| 是否最优 | ✅ 最短路径 | ✅ 可纳启发式 |
| 实际速度 | 中等 | 通常更快 |
| 适用场景 | 无权图 | 带启发式搜索 |

## 演示截图

![迷宫遥控器界面](img/maze_remote_ui.png)
![BFS寻路结果](img/bfs_path_result.png)

---

## 踩坑记录

| 问题 | 原因 | 解决方案 |
|:---|:---|:---|
| 手机无法访问服务器 | 不在同一局域网 | 同一 WiFi 或 Tailscale 组网 |
| WebSocket 连接被拒 | 5000 端口未开放 | `sudo ufw allow 5000` |
| Canvas 手机显示模糊 | 未适配 devicePixelRatio | JS 动态计算 cellSize |
| 触摸事件触发两次 | click + touchstart | `event.preventDefault()` |

---

## 总结

本项目完整实现了 Week 14 的所有要求：手机 Web 遥控界面、迷宫模块、自动寻路算法、前后端实时通信。系统架构清晰、代码注释完整、算法实现规范。

项目代码位于 `maze_app/` 子目录，详细报告见 `maze_app/week14_report.md`。
