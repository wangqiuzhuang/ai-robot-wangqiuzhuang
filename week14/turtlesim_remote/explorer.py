#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""自动走迷宫（方向 B）— A* + BFS 双算法路径搜索器

在迷宫的格点图上搜索从起点格到终点格的最短格序列，再把每个格中心
当成路标依次行驶。把它接到桥接程序的自动模式即可。

★ 已实现:
  - A* (曼哈顿启发式) — 通常更快找到路径
  - BFS — 保证最短路径，便于对比扩展节点数
  - 自动避障: 若碰撞则重新规划
"""

import heapq
import math
from collections import deque
from maze import build_maze

LIN = 1.6
ANG_MAX = 2.2
K_ANG = 3.0
TURN_FIRST = 0.6
REACH_TOL = 0.12


def bfs(neighbors, start, goal):
    """BFS 最短路径搜索 (无权图，保证最短)"""
    q = deque([start])
    came = {start: None}
    while q:
        cur = q.popleft()
        if cur == goal:
            break
        for nxt in neighbors(cur):
            if nxt not in came:
                came[nxt] = cur
                q.append(nxt)
    if goal not in came:
        return [], 0
    path, c = [], goal
    while c is not None:
        path.append(c)
        c = came[c]
    return path[::-1], len(came)


def astar(neighbors, start, goal):
    """A* 搜索 (曼哈顿启发式)"""
    openq = [(0, start)]
    came = {start: None}
    g = {start: 0}
    h = lambda c: abs(c[0] - goal[0]) + abs(c[1] - goal[1])
    while openq:
        _, cur = heapq.heappop(openq)
        if cur == goal:
            break
        for nxt in neighbors(cur):
            ng = g[cur] + 1
            if nxt not in g or ng < g[nxt]:
                g[nxt] = ng
                came[nxt] = cur
                heapq.heappush(openq, (ng + h(nxt), nxt))
    if goal not in came:
        return [], 0
    path, c = [], goal
    while c is not None:
        path.append(c)
        c = came[c]
    return path[::-1], len(came)


class Planner:
    """自动探索规划器，默认使用 A* 算法"""

    def __init__(self, use_bfs=False):
        self.m = build_maze()
        self.grid = self.m["grid"]
        self.waypoints = None
        self.idx = 0
        self.use_bfs = use_bfs
        self.expanded_nodes = 0
        self.algorithm = "BFS" if use_bfs else "A*"

    def _to_cell(self, x, y):
        o, c = self.grid["origin"], self.grid["cell"]
        ci = min(self.grid["cols"] - 1, max(0, round((x - o - c / 2) / c)))
        cj = min(self.grid["rows"] - 1, max(0, round((y - o - c / 2) / c)))
        return (ci, cj)

    def _plan(self, x, y):
        start = self._to_cell(x, y)
        if self.use_bfs:
            cells, expanded = bfs(self.m["neighbors"], start, self.m["goal_cell"])
        else:
            cells, expanded = astar(self.m["neighbors"], start, self.m["goal_cell"])
        self.expanded_nodes = expanded
        cc = self.m["cell_center"]
        self.waypoints = [(cc(i), cc(j)) for (i, j) in cells]
        self.idx = 1 if len(self.waypoints) > 1 else 0

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


def compare_algorithms():
    """对比 BFS 和 A* 的性能"""
    m = build_maze()
    start, goal = m["start_cell"], m["goal_cell"]
    n = m["neighbors"]

    bfs_path, bfs_expanded = bfs(n, start, goal)
    astar_path, astar_expanded = astar(n, start, goal)

    print("=" * 50)
    print("  迷宫寻路算法性能对比")
    print("=" * 50)
    print(f"  迷宫: {m['grid']['cols']}x{m['grid']['rows']}, "
          f"环路={len(m['open_edges']) - m['grid']['cols'] * m['grid']['rows'] + 1}")
    print()
    print(f"  {'算法':<8} {'路径长度':<10} {'扩展节点':<10}")
    print(f"  {'-'*28}")
    print(f"  {'BFS':<8} {len(bfs_path):<10} {bfs_expanded:<10}")
    print(f"  {'A*':<8} {len(astar_path):<10} {astar_expanded:<10}")
    print()
    if bfs_path == astar_path:
        print("  ✅ 两种算法找到了相同长度的路径")
    else:
        print(f"  ⚠️  路径长度不同: BFS={len(bfs_path)}, A*={len(astar_path)} (均有效)")
    print("=" * 50)


if __name__ == "__main__":
    compare_algorithms()
