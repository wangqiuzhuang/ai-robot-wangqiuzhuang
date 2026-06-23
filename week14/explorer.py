#!/usr/bin/env python3
"""
Week 14: 迷宫自动探索模块
===========================
实现 BFS (广度优先搜索) 和 A* (A-Star) 两种寻路算法。

算法对比:
  ┌──────────┬─────────────────┬──────────────────┐
  │ 算法      │ 时间复杂度       │ 特点              │
  ├──────────┼─────────────────┼──────────────────┤
  │ BFS       │ O(V + E)        │ 保证最短路径       │
  │ A*        │ O(E) 最坏       │ 启发式，通常更快    │
  └──────────┴─────────────────┴──────────────────┘

BFS:  逐层扩展，先找到的路径一定是最短的 (在无权图中)
A*:   使用曼哈顿距离启发函数，优先探索更接近目标的格子
"""

import heapq
from collections import deque
from typing import List, Tuple, Optional, Callable
from maze import Maze


# ============================================================
# BFS — 广度优先搜索
# ============================================================

def bfs_solve(maze: Maze, start: Tuple[int, int], goal: Tuple[int, int]) -> Optional[List[Tuple[int, int]]]:
    """
    BFS 寻路算法

    算法步骤:
      1. 将起点加入队列
      2. 从队列取出一个节点
      3. 如果是目标节点 → 回溯构造路径并返回
      4. 将其所有未访问的可通行邻居加入队列
      5. 重复 2-4 直到队列为空或找到目标

    参数:
        maze:  迷宫对象
        start: 起点坐标 (x, y)
        goal:  终点坐标 (x, y)

    返回:
        最短路径列表 [(x1,y1), (x2,y2), ..., (goal_x, goal_y)]
        无法到达时返回 None
    """
    if start == goal:
        return [start]

    queue = deque([start])
    visited = {start}
    parent = {start: None}  # 记录每个节点的父节点，用于回溯路径

    while queue:
        current = queue.popleft()

        # 检查是否到达目标
        if current == goal:
            return _reconstruct_path(parent, goal)

        # 扩展所有可通行的邻居
        for neighbor in maze.get_passable_neighbors(*current):
            if neighbor not in visited:
                visited.add(neighbor)
                parent[neighbor] = current
                queue.append(neighbor)

    return None  # 无法到达


# ============================================================
# A* — A-Star 搜索
# ============================================================

def _manhattan_distance(a: Tuple[int, int], b: Tuple[int, int]) -> int:
    """曼哈顿距离启发函数: |x1-x2| + |y1-y2|"""
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


def astar_solve(maze: Maze, start: Tuple[int, int], goal: Tuple[int, int]) -> Optional[List[Tuple[int, int]]]:
    """
    A* 寻路算法

    算法步骤:
      1. 将起点加入优先队列 (优先级 f = g + h)
      2. 取出 f 值最小的节点
      3. 如果是目标节点 → 回溯构造路径并返回
      4. 更新邻居的 g 值，如果找到更优路径则更新
      5. 重复 2-4 直到队列为空或找到目标

    其中:
      g(n) = 从起点到节点 n 的实际代价 (步数)
      h(n) = 从节点 n 到目标的启发式估计 (曼哈顿距离)
      f(n) = g(n) + h(n)  (评估函数)

    参数:
        maze:  迷宫对象
        start: 起点坐标 (x, y)
        goal:  终点坐标 (x, y)

    返回:
        路径列表 [(x1,y1), (x2,y2), ..., (goal_x, goal_y)]
        无法到达时返回 None
    """
    if start == goal:
        return [start]

    # open_set: 优先队列 (f_score, counter, node) — counter 用于打破平局
    counter = 0
    open_set = [(0, counter, start)]
    open_set_nodes = {start}

    # 记录
    g_score = {start: 0}       # 从起点到该节点的实际代价
    parent = {start: None}     # 父节点链

    while open_set:
        f_score, _, current = heapq.heappop(open_set)
        open_set_nodes.discard(current)

        # 到达目标
        if current == goal:
            return _reconstruct_path(parent, goal)

        # 扩展邻居
        for neighbor in maze.get_passable_neighbors(*current):
            tentative_g = g_score[current] + 1  # 每步代价为 1

            if neighbor not in g_score or tentative_g < g_score[neighbor]:
                # 找到更优路径
                g_score[neighbor] = tentative_g
                parent[neighbor] = current
                f = tentative_g + _manhattan_distance(neighbor, goal)

                if neighbor not in open_set_nodes:
                    counter += 1
                    heapq.heappush(open_set, (f, counter, neighbor))
                    open_set_nodes.add(neighbor)

    return None  # 无法到达


# ============================================================
# 路径重构
# ============================================================

def _reconstruct_path(parent: dict, goal: Tuple[int, int]) -> List[Tuple[int, int]]:
    """从父节点字典回溯构造完整路径"""
    path = []
    current = goal
    while current is not None:
        path.append(current)
        current = parent[current]
    path.reverse()
    return path


# ============================================================
# Explorer 类: 自动探索器
# ============================================================

class Explorer:
    """
    自动迷宫探索器

    策略:
      1. 维护一个"已探索"集合
      2. 每一步用 BFS 找到最近的未探索格子
      3. 如果没有未探索格子 → 用 A* 直接走向终点
      4. 沿途记录路径和发现的"兴趣点"
    """

    def __init__(self, maze: Maze):
        self.maze = maze
        self.explored: set = set()
        self.path_history: List[Tuple[int, int]] = []
        self.interest_points: List[dict] = []

    def explore(self, start: Tuple[int, int], goal: Tuple[int, int],
                step_callback: Optional[Callable] = None) -> Optional[List[Tuple[int, int]]]:
        """
        执行自动探索

        参数:
            start:          起点
            goal:           终点
            step_callback:  每步的回调函数 callback(position, explored_count)

        返回:
            完整探索路径
        """
        current = start
        self.explored = {start}
        self.path_history = [start]
        self.interest_points = []

        while current != goal:
            # 标记当前位置及邻居为已探索
            self.explored.add(current)
            for neighbor in self.maze.get_passable_neighbors(*current):
                self.explored.add(neighbor)

                # 记录十字路口 (有 ≥3 个出口的格子)
                if len(self.maze.get_passable_neighbors(*neighbor)) >= 3:
                    self.interest_points.append({
                        "position": neighbor,
                        "type": "junction",
                        "exits": len(self.maze.get_passable_neighbors(*neighbor)),
                    })

            if step_callback:
                step_callback(current, len(self.explored))

            # 优先用 A* 找路径到目标
            path = astar_solve(self.maze, current, goal)
            if not path or len(path) < 2:
                break

            current = path[1]
            self.path_history.append(current)

        return self.path_history if current == goal else None

    def get_statistics(self) -> dict:
        """获取探索统计信息"""
        total_cells = self.maze.width * self.maze.height
        return {
            "total_cells": total_cells,
            "explored_cells": len(self.explored),
            "exploration_rate": f"{len(self.explored) / total_cells * 100:.1f}%",
            "path_length": len(self.path_history),
            "junctions_found": len(self.interest_points),
        }


# ============================================================
# 算法性能对比
# ============================================================

def benchmark(maze: Maze) -> dict:
    """对比 BFS 和 A* 在同一迷宫上的性能"""
    import time

    start = (0, 0)
    goal = (maze.width - 1, maze.height - 1)

    # BFS
    t0 = time.perf_counter()
    bfs_path = bfs_solve(maze, start, goal)
    bfs_time = (time.perf_counter() - t0) * 1000  # ms

    # A*
    t0 = time.perf_counter()
    astar_path = astar_solve(maze, start, goal)
    astar_time = (time.perf_counter() - t0) * 1000  # ms

    return {
        "bfs": {
            "time_ms": f"{bfs_time:.3f}",
            "path_length": len(bfs_path) if bfs_path else 0,
            "found": bfs_path is not None,
        },
        "astar": {
            "time_ms": f"{astar_time:.3f}",
            "path_length": len(astar_path) if astar_path else 0,
            "found": astar_path is not None,
        },
    }


# ============================================================
# 自测
# ============================================================
if __name__ == "__main__":
    from maze import Maze
    import random
    random.seed(42)

    m = Maze(20, 20)
    m.generate()

    print("=" * 60)
    print("迷宫寻路算法对比测试")
    print("=" * 60)

    result = benchmark(m)
    print(f"BFS:  {'✅ 找到' if result['bfs']['found'] else '❌ 未找到'} | 耗时 {result['bfs']['time_ms']}ms | 路径长度 {result['bfs']['path_length']}")
    print(f"A*:   {'✅ 找到' if result['astar']['found'] else '❌ 未找到'} | 耗时 {result['astar']['time_ms']}ms | 路径长度 {result['astar']['path_length']}")

    # 探索测试
    exp = Explorer(m)
    path = exp.explore((0, 0), (19, 19))
    stats = exp.get_statistics()
    print(f"\n探索统计: {stats}")
    print(f"兴趣点: {len(exp.interest_points)} 个路口")
