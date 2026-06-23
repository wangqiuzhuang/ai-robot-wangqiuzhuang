#!/usr/bin/env python3
"""
Week 14: turtlesim 遥控迷宫 — WebSocket 桥接程序 (方向 B)

单一常驻程序：同时运行 aiohttp WebSocket 服务器 + ROS2 节点。
- 接收手机网页的控制命令 (前进/后退/左转/右转/停止)
- 发布 /turtle1/cmd_vel 驱动小乌龟
- 内置迷宫边界 + 障碍物碰撞检测

运行方式:
  终端1: source /opt/ros/humble/setup.bash && ros2 run turtlesim turtlesim_node
  终端2: source /opt/ros/humble/setup.bash && pip install aiohttp && python3 turtlesim_web_bridge.py
  手机浏览器: http://<Tailscale_IP>:8080
"""

import asyncio
import json
import math
import threading
from pathlib import Path

from aiohttp import WSMsgType, web
from geometry_msgs.msg import Twist
import rclpy
from rclpy.node import Node
from turtlesim.msg import Pose
from turtlesim.srv import TeleportAbsolute

from maze import build_maze

HOST = "0.0.0.0"
PORT = 8080
CONTROL_PERIOD = 0.1
TURTLE_RADIUS = 0.45
_MAZE = build_maze()
MAZE_BOUNDS = _MAZE["bounds"]
START_POSE = _MAZE["start"]
GOAL_REGION = _MAZE["goal"]
OBSTACLES = _MAZE["obstacles"]


class TurtleWebBridge(Node):
    """ROS2 节点 + WebSocket 桥接: 手机手动遥控"""

    def __init__(self):
        super().__init__("turtlesim_web_bridge")
        self.publisher = self.create_publisher(Twist, "/turtle1/cmd_vel", 10)
        self.subscription = self.create_subscription(
            Pose, "/turtle1/pose", self.on_pose, 10
        )
        self.current_linear = 0.0
        self.current_angular = 0.0
        self.applied_linear = 0.0
        self.applied_angular = 0.0
        self.current_pose = {"x": 0.0, "y": 0.0, "theta": 0.0}
        self.blocked = False
        self.block_reason = "waiting_for_pose"
        self.goal_reached = False
        self.teleport_client = self.create_client(
            TeleportAbsolute, "/turtle1/teleport_absolute"
        )
        self.timer = self.create_timer(CONTROL_PERIOD, self.publish_command)
        self.init_timer = self.create_timer(0.5, self.try_initialize_maze)
        self.maze_initialized = False

    def on_pose(self, msg):
        self.current_pose = {
            "x": round(msg.x, 3),
            "y": round(msg.y, 3),
            "theta": round(msg.theta, 3),
        }
        self.goal_reached = self.is_inside_goal(msg.x, msg.y)
        if self.goal_reached:
            self.current_linear = 0.0
            self.current_angular = 0.0
            self.applied_linear = 0.0
            self.applied_angular = 0.0
            self.blocked = False
            self.block_reason = "goal_reached"

    def set_command(self, linear, angular):
        self.current_linear = float(linear)
        self.current_angular = float(angular)

    def stop(self):
        self.set_command(0.0, 0.0)

    def try_initialize_maze(self):
        if self.maze_initialized:
            return
        if not self.teleport_client.wait_for_service(timeout_sec=0.0):
            return
        self.reset_to_start()
        self.maze_initialized = True
        self.init_timer.cancel()

    def reset_to_start(self):
        if not self.teleport_client.wait_for_service(timeout_sec=0.5):
            self.get_logger().warning("Teleport service not ready yet.")
            return
        req = TeleportAbsolute.Request()
        req.x = float(START_POSE["x"])
        req.y = float(START_POSE["y"])
        req.theta = float(START_POSE["theta"])
        self.teleport_client.call_async(req)
        self.current_linear = 0.0
        self.current_angular = 0.0
        self.applied_linear = 0.0
        self.applied_angular = 0.0
        self.blocked = False
        self.block_reason = "reset_to_start"
        self.goal_reached = False

    def is_inside_goal(self, x, y):
        dx = x - GOAL_REGION["x"]
        dy = y - GOAL_REGION["y"]
        return dx * dx + dy * dy <= GOAL_REGION["radius"] ** 2

    def would_hit_boundary(self, x, y):
        return not (
            MAZE_BOUNDS["min_x"] + TURTLE_RADIUS <= x <= MAZE_BOUNDS["max_x"] - TURTLE_RADIUS
            and MAZE_BOUNDS["min_y"] + TURTLE_RADIUS <= y <= MAZE_BOUNDS["max_y"] - TURTLE_RADIUS
        )

    def would_hit_obstacle(self, x, y):
        for obstacle in OBSTACLES:
            inflated_min_x = obstacle["x"] - TURTLE_RADIUS
            inflated_max_x = obstacle["x"] + obstacle["w"] + TURTLE_RADIUS
            inflated_min_y = obstacle["y"] - TURTLE_RADIUS
            inflated_max_y = obstacle["y"] + obstacle["h"] + TURTLE_RADIUS
            if inflated_min_x <= x <= inflated_max_x and inflated_min_y <= y <= inflated_max_y:
                return True
        return False

    def compute_safe_motion(self):
        x = self.current_pose["x"]
        y = self.current_pose["y"]
        theta = self.current_pose["theta"]

        if x == 0.0 and y == 0.0:
            self.blocked = False
            self.block_reason = "waiting_for_pose"
            return 0.0, self.current_angular

        next_x = x + self.current_linear * CONTROL_PERIOD * math.cos(theta)
        next_y = y + self.current_linear * CONTROL_PERIOD * math.sin(theta)

        safe_linear = self.current_linear
        if self.goal_reached:
            safe_linear = 0.0
            self.blocked = False
            self.block_reason = "goal_reached"
        elif self.would_hit_boundary(next_x, next_y):
            safe_linear = 0.0
            self.blocked = True
            self.block_reason = "boundary"
        elif self.would_hit_obstacle(next_x, next_y):
            safe_linear = 0.0
            self.blocked = True
            self.block_reason = "obstacle"
        else:
            self.blocked = False
            self.block_reason = "clear"

        return safe_linear, self.current_angular

    def publish_command(self):
        safe_linear, safe_angular = self.compute_safe_motion()
        msg = Twist()
        msg.linear.x = safe_linear
        msg.angular.z = safe_angular
        self.applied_linear = safe_linear
        self.applied_angular = safe_angular
        self.publisher.publish(msg)

    def get_state(self):
        return {
            "pose": dict(self.current_pose),
            "command": {
                "linear": self.current_linear,
                "angular": self.current_angular,
            },
            "applied_command": {
                "linear": self.applied_linear,
                "angular": self.applied_angular,
            },
            "rule": {
                "blocked": self.blocked,
                "reason": self.block_reason,
                "goal_reached": self.goal_reached,
            },
            "maze": {
                "bounds": dict(MAZE_BOUNDS),
                "start": dict(START_POSE),
                "goal": dict(GOAL_REGION),
                "obstacles": list(OBSTACLES),
                "turtle_radius": TURTLE_RADIUS,
            },
        }


# ── Web 服务 ────────────────────────────────────────────

def spin_ros(node):
    rclpy.spin(node)


async def index(request):
    html = Path(__file__).with_name("index.html").read_text(encoding="utf-8")
    return web.Response(text=html, content_type="text/html")


async def websocket_handler(request):
    ws = web.WebSocketResponse()
    await ws.prepare(request)

    app = request.app
    bridge = app["bridge"]
    app["clients"].add(ws)
    await ws.send_json({"type": "state", "data": bridge.get_state()})

    try:
        async for msg in ws:
            if msg.type != WSMsgType.TEXT:
                continue
            data = json.loads(msg.data)
            msg_type = data.get("type")

            if msg_type == "command":
                bridge.set_command(data.get("linear", 0.0), data.get("angular", 0.0))
            elif msg_type == "stop":
                bridge.stop()
            elif msg_type == "reset":
                bridge.reset_to_start()

            await ws.send_json({"type": "state", "data": bridge.get_state()})
    finally:
        app["clients"].discard(ws)
    return ws


async def broadcast_loop(app):
    while True:
        state_json = json.dumps({"type": "state", "data": app["bridge"].get_state()})
        stale = []
        for ws in app["clients"]:
            if ws.closed:
                stale.append(ws)
                continue
            await ws.send_str(state_json)
        for ws in stale:
            app["clients"].discard(ws)
        await asyncio.sleep(0.2)


async def on_startup(app):
    rclpy.init()
    bridge = TurtleWebBridge()
    app["bridge"] = bridge
    app["clients"] = set()
    ros_thread = threading.Thread(target=spin_ros, args=(bridge,), daemon=True)
    ros_thread.start()
    app["ros_thread"] = ros_thread
    app["broadcast_task"] = asyncio.create_task(broadcast_loop(app))


async def on_cleanup(app):
    app["broadcast_task"].cancel()
    try:
        await app["broadcast_task"]
    except asyncio.CancelledError:
        pass
    app["bridge"].destroy_node()
    rclpy.shutdown()
    app["ros_thread"].join(timeout=1.0)


def main():
    app = web.Application()
    app.router.add_get("/", index)
    app.router.add_get("/ws", websocket_handler)
    app.on_startup.append(on_startup)
    app.on_cleanup.append(on_cleanup)

    print(f"🐢 turtlesim 迷宫桥接程序启动: http://{HOST}:{PORT}")
    print(f"   手机访问: http://<Tailscale_IP>:{PORT}")
    web.run_app(app, host=HOST, port=PORT)


if __name__ == "__main__":
    main()
