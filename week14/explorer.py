#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""自动走迷宫（方向 B）——路径搜索算法对比与自动导航。

支持三种路径搜索算法：
  - BFS：广度优先，保证最短路径（无权图），扩展节点多
  - Dijkstra：考虑代价（离墙越近代价越高），路径更安全但未必最短
  - A*：曼哈顿启发式，收敛最快，扩展节点最少

接入方式（在 turtlesim_web_bridge.py 里）：
    from explorer import Planner
    self.explorer = Planner(algorithm="astar")
    self.auto = False
    # 在 publish_command() 里，若 self.auto:
    lin, ang = self.explorer.decide(self.get_state())
    self.set_command(lin, ang)
"""
import heapq
import math
from collections import deque
from maze import build_maze

LIN = 1.6
ANG_MAX = 2.2
K_ANG = 3.0          # 比例转向增益
TURN_FIRST = 0.6     # 朝向误差大于此值时先原地转
REACH_TOL = 0.12

# ── 路径搜索算法 ──────────────────────────────────────────

def bfs(neighbors, start, goal):
    """BFS：无权图最短路径（扩展节点最多，但路径最短）。"""
    q = deque([start])
    came = {start: None}
    nodes_expanded = 0
    while q:
        cur = q.popleft()
        nodes_expanded += 1
        if cur == goal:
            break
        for nxt in neighbors(cur):
            if nxt not in came:
                came[nxt] = cur
                q.append(nxt)
    if goal not in came:
        return [], nodes_expanded
    path, c = [], goal
    while c is not None:
        path.append(c)
        c = came[c]
    return path[::-1], nodes_expanded


def dijkstra(neighbors, start, goal, cost_fn=None):
    """Dijkstra：有权图最短路径，cost_fn(cell, nxt) 返回边权重。"""
    openq = [(0, start)]
    came = {start: None}
    g = {start: 0}
    nodes_expanded = 0
    while openq:
        g_cur, cur = heapq.heappop(openq)
        nodes_expanded += 1
        if cur == goal:
            break
        for nxt in neighbors(cur):
            edge_cost = cost_fn(cur, nxt) if cost_fn else 1
            ng = g_cur + edge_cost
            if nxt not in g or ng < g[nxt]:
                g[nxt] = ng
                came[nxt] = cur
                heapq.heappush(openq, (ng, nxt))
    if goal not in came:
        return [], nodes_expanded
    path, c = [], goal
    while c is not None:
        path.append(c)
        c = came[c]
    return path[::-1], nodes_expanded


def astar(neighbors, start, goal):
    """A*：曼哈顿启发式，通常扩展节点最少。"""
    openq = [(0, start)]
    came = {start: None}
    g = {start: 0}
    h = lambda c: abs(c[0] - goal[0]) + abs(c[1] - goal[1])
    nodes_expanded = 0
    while openq:
        _, cur = heapq.heappop(openq)
        nodes_expanded += 1
        if cur == goal:
            break
        for nxt in neighbors(cur):
            ng = g[cur] + 1
            if nxt not in g or ng < g[nxt]:
                g[nxt] = ng
                came[nxt] = cur
                heapq.heappush(openq, (ng + h(nxt), nxt))
    if goal not in came:
        return [], nodes_expanded
    path, c = [], goal
    while c is not None:
        path.append(c)
        c = came[c]
    return path[::-1], nodes_expanded


# ── Planner 控制器 ──────────────────────────────────────────

class Planner:
    def __init__(self, algorithm="astar"):
        self.m = build_maze()
        self.grid = self.m["grid"]
        self.waypoints = None
        self.idx = 0
        self.algorithm = algorithm
        self.stats = {}                 # 上次规划的统计信息

    def _to_cell(self, x, y):
        o, c = self.grid["origin"], self.grid["cell"]
        ci = min(self.grid["cols"] - 1, max(0, round((x - o - c / 2) / c)))
        cj = min(self.grid["rows"] - 1, max(0, round((y - o - c / 2) / c)))
        return (ci, cj)

    def _plan(self, x, y):
        """用选定算法规划路径，同时记录统计信息用于对比。"""
        start = self._to_cell(x, y)
        goal = self.m["goal_cell"]

        if self.algorithm == "bfs":
            cells, expanded = bfs(self.m["neighbors"], start, goal)
        elif self.algorithm == "dijkstra":
            # 代价函数：靠近墙的格代价更高（安全裕度）
            def cost_fn(cur, nxt):
                i, j = nxt
                cols, rows = self.grid["cols"], self.grid["rows"]
                # 边缘格代价略高，让路径倾向于走中间
                if i == 0 or i == cols - 1 or j == 0 or j == rows - 1:
                    return 1.5
                return 1.0
            cells, expanded = dijkstra(self.m["neighbors"], start, goal, cost_fn)
        else:   # astar (default)
            cells, expanded = astar(self.m["neighbors"], start, goal)

        self.stats = {
            "algorithm": self.algorithm,
            "nodes_expanded": expanded,
            "path_length": len(cells),
        }

        cc = self.m["cell_center"]
        self.waypoints = [(cc(i), cc(j)) for (i, j) in cells]
        self.idx = 1 if len(self.waypoints) > 1 else 0

    def set_algorithm(self, algo):
        """运行时切换算法，下次规划生效。"""
        if algo in ("bfs", "dijkstra", "astar"):
            self.algorithm = algo
            self.waypoints = None   # 强制重新规划

    def decide(self, state):
        if state.get("rule", {}).get("goal_reached"):
            return 0.0, 0.0
        x, y = state["pose"]["x"], state["pose"]["y"]
        theta = state["pose"]["theta"]
        if x == 0.0 and y == 0.0:
            return 0.0, 0.0
        if self.waypoints is None:
            self._plan(x, y)
        if not self.waypoints or self.idx >= len(self.waypoints):
            return 0.0, 0.0
        tx, ty = self.waypoints[self.idx]
        if math.hypot(tx - x, ty - y) < REACH_TOL:
            self.idx += 1
            return 0.0, 0.0
        desired = math.atan2(ty - y, tx - x)
        err = math.atan2(math.sin(desired - theta), math.cos(desired - theta))
        ang = max(-ANG_MAX, min(ANG_MAX, K_ANG * err))
        lin = 0.0 if abs(err) > TURN_FIRST else LIN
        return lin, ang


# ── 自测（算法对比）───────────────────────────────────────

if __name__ == "__main__":
    m = build_maze()
    print(f"Maze: {m['grid']['cols']}x{m['grid']['rows']}  "
          f"loops={len(m['open_edges']) - m['grid']['cols'] * m['grid']['rows'] + 1}")
    print()

    for algo in ("bfs", "dijkstra", "astar"):
        p = Planner(algorithm=algo)
        p._plan(m["start"]["x"], m["start"]["y"])
        s = p.stats
        print(f"{algo:>10}:  expanded={s['nodes_expanded']:>3}  "
              f"path_len={s['path_length']:>2}  "
              f"waypoints={len(p.waypoints)}")
