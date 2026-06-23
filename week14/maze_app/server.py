#!/usr/bin/env python3
"""
Week 14: Phone-Controlled Maze Robot — WebSocket Server
========================================================
双向通信桥梁: 手机浏览器 ←→ WebSocket ←→ Python 机器人控制

架构:
  Phone (index.html) ──WebSocket──▶ server.py
                                        │
                        ┌───────────────┼───────────────┐
                        ▼               ▼               ▼
                   maze.py        explorer.py      robot control
                   (迷宫生成)     (BFS/A*寻路)     (PyBullet/turtlesim)

启动方式:
    python3 server.py
    手机浏览器访问: http://<server-ip>:5000
"""

import asyncio
import json
import logging
import os
import sys
import time
from pathlib import Path

# ── Web 服务 ──────────────────────────────────────────────
import tornado.ioloop
import tornado.web
import tornado.websocket
import tornado.escape

# ── 迷宫 & 寻路 ───────────────────────────────────────────
from maze import Maze, MAZE_SIZE
from explorer import Explorer, bfs_solve, astar_solve

logging.basicConfig(level=logging.INFO, format='[%(asctime)s] %(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

# ============================================================
# 全局状态
# ============================================================
connected_clients: set = set()
maze_instance: Maze = None
robot_position = (0, 0)          # 机器人在迷宫中的当前位置
robot_path: list = []            # 已行走的路径
auto_exploring = False
explore_task = None


# ============================================================
# WebSocket 处理器
# ============================================================
class MazeWebSocket(tornado.websocket.WebSocketHandler):
    """处理手机浏览器与服务器之间的实时双向通信"""

    def check_origin(self, origin):
        return True  # 允许跨域访问

    def open(self):
        connected_clients.add(self)
        logger.info(f"📱 客户端连接: {self.request.remote_ip} (当前 {len(connected_clients)} 个连接)")

        # 发送初始状态
        self.write_message(json.dumps({
            "type": "connected",
            "message": "✅ 已连接到迷宫机器人服务器",
            "maze": maze_instance.to_dict() if maze_instance else None,
            "robot_position": list(robot_position),
        }))

    def on_close(self):
        connected_clients.discard(self)
        logger.info(f"📴 客户端断开: {self.request.remote_ip} (剩余 {len(connected_clients)} 个连接)")

    def on_message(self, message):
        """接收手机端发来的控制指令"""
        global robot_position, robot_path, auto_exploring

        try:
            data = json.loads(message)
            cmd = data.get("command", "")
            logger.info(f"📨 收到指令: {cmd} | 数据: {data}")

            # ── 手动控制: 方向键 ──
            if cmd == "move":
                direction = data.get("direction", "up")
                new_pos = _move_robot(robot_position, direction)
                if maze_instance and maze_instance.is_walkable(*new_pos):
                    robot_position = new_pos
                    robot_path.append(new_pos)
                    _broadcast_state(f"🤖 移动到 {new_pos}")
                else:
                    _broadcast_state("⛔ 撞墙了!", "wall_hit")

            # ── 生成新迷宫 ──
            elif cmd == "generate_maze":
                global maze_instance
                maze_instance = Maze(MAZE_SIZE, MAZE_SIZE)
                maze_instance.generate()
                robot_position = (0, 0)
                robot_path = [(0, 0)]
                _broadcast_state("🏗️ 新迷宫已生成", "maze_generated")

            # ── 自动寻路 (BFS) ──
            elif cmd == "auto_bfs":
                if maze_instance:
                    path = bfs_solve(maze_instance, robot_position, (MAZE_SIZE - 1, MAZE_SIZE - 1))
                    if path:
                        asyncio.ensure_future(_animate_path(path))
                    else:
                        _broadcast_state("❌ BFS 找不到路径", "no_path")

            # ── 自动寻路 (A*) ──
            elif cmd == "auto_astar":
                if maze_instance:
                    path = astar_solve(maze_instance, robot_position, (MAZE_SIZE - 1, MAZE_SIZE - 1))
                    if path:
                        asyncio.ensure_future(_animate_path(path))
                    else:
                        _broadcast_state("❌ A* 找不到路径", "no_path")

            # ── 自动探索 ──
            elif cmd == "auto_explore":
                auto_exploring = True
                explorer = Explorer(maze_instance)
                asyncio.ensure_future(_auto_explore(explorer))

            # ── 停止自动探索 ──
            elif cmd == "stop":
                auto_exploring = False
                _broadcast_state("⏹️ 已停止")

            # ── 重置机器人位置 ──
            elif cmd == "reset":
                robot_position = (0, 0)
                robot_path = [(0, 0)]
                auto_exploring = False
                _broadcast_state("🔄 已重置到起点")

            # ── 获取当前状态 ──
            elif cmd == "status":
                _broadcast_state("📊 状态查询")

            else:
                self.write_message(json.dumps({
                    "type": "error",
                    "message": f"未知指令: {cmd}"
                }))

        except json.JSONDecodeError:
            self.write_message(json.dumps({"type": "error", "message": "无效的 JSON 格式"}))


# ============================================================
# 辅助函数
# ============================================================
def _move_robot(pos, direction):
    """计算移动后的新位置"""
    x, y = pos
    moves = {"up": (x, y - 1), "down": (x, y + 1),
             "left": (x - 1, y), "right": (x + 1, y)}
    return moves.get(direction, pos)


def _broadcast_state(message, event_type="state_update"):
    """向所有连接的客户端广播当前状态"""
    payload = {
        "type": event_type,
        "message": message,
        "maze": maze_instance.to_dict() if maze_instance else None,
        "robot_position": list(robot_position),
        "robot_path": [list(p) for p in robot_path],
        "auto_exploring": auto_exploring,
    }
    for client in connected_clients:
        try:
            client.write_message(json.dumps(payload))
        except Exception:
            pass


async def _animate_path(path):
    """逐步动画展示寻路结果"""
    global robot_position, robot_path
    for pos in path[1:]:  # 跳过起点
        await asyncio.sleep(0.3)
        robot_position = pos
        robot_path.append(pos)
        _broadcast_state(f"🚶 沿路径移动: {pos}", "path_step")
    _broadcast_state("🎉 到达终点!", "goal_reached")


async def _auto_explore(explorer):
    """自动探索迷宫直到完成"""
    global robot_position, robot_path, auto_exploring
    start = robot_position
    goal = (MAZE_SIZE - 1, MAZE_SIZE - 1)

    logger.info(f"🔍 开始自动探索: {start} → {goal}")

    while auto_exploring and robot_position != goal:
        # 用 BFS 找到到未探索区域最近的路径
        path = bfs_solve(maze_instance, robot_position, goal)
        if not path or len(path) < 2:
            break

        next_pos = path[1]
        robot_position = next_pos
        robot_path.append(next_pos)
        _broadcast_state(f"🔍 探索中: {next_pos}", "explore_step")
        await asyncio.sleep(0.4)

    if robot_position == goal:
        _broadcast_state("🏆 迷宫探索完成!", "explore_done")
    else:
        _broadcast_state("⏸️ 探索已暂停", "explore_paused")
    auto_exploring = False


# ============================================================
# HTTP 处理器
# ============================================================
class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.render("index.html")


# ============================================================
# 应用启动
# ============================================================
def make_app():
    settings = {
        "static_path": os.path.join(os.path.dirname(__file__), "static"),
        "template_path": os.path.dirname(__file__),
        "debug": True,
    }
    return tornado.web.Application([
        (r"/", MainHandler),
        (r"/ws", MazeWebSocket),
    ], **settings)


if __name__ == "__main__":
    # 初始化迷宫
    maze_instance = Maze(MAZE_SIZE, MAZE_SIZE)
    maze_instance.generate()
    robot_position = (0, 0)
    robot_path = [(0, 0)]

    app = make_app()
    port = int(os.environ.get("PORT", 5000))
    logger.info(f"🚀 迷宫机器人服务器启动: http://0.0.0.0:{port}")
    logger.info(f"📱 手机浏览器访问: http://<你的IP>:{port}")
    logger.info(f"🔌 WebSocket 端点: ws://<你的IP>:{port}/ws")
    app.listen(port)
    tornado.ioloop.IOLoop.current().start()
