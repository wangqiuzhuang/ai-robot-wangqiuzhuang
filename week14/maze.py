#!/usr/bin/env python3
"""
Week 14: 迷宫生成模块
======================
实现基于递归回溯算法 (Recursive Backtracking) 的迷宫生成。

算法原理:
  1. 从起点开始，将当前格子标记为已访问
  2. 随机选择一个未访问的相邻格子
  3. 打通当前格子和选中格子之间的墙壁
  4. 递归进入选中格子
  5. 当所有相邻格子都已访问时回溯

生成的迷宫保证:
  - 所有格子连通 (无孤立区域)
  - 任意两点间存在唯一路径 (完美迷宫)
"""

import random
from typing import List, Tuple, Optional

# 迷宫尺寸 (可配置)
MAZE_SIZE = 10

# 方向定义: (dx, dy, 对面的墙方向)
DIRECTIONS = {
    "N":  (0, -1, "S"),   # 北
    "S":  (0, 1, "N"),    # 南
    "E":  (1, 0, "W"),    # 东
    "W":  (-1, 0, "E"),   # 西
}


class Cell:
    """迷宫中的一个格子"""

    def __init__(self, x: int, y: int):
        self.x = x
        self.y = y
        # 四面墙壁: N, S, E, W (True = 墙壁存在)
        self.walls = {"N": True, "S": True, "E": True, "W": True}
        self.visited = False

    def remove_wall(self, direction: str):
        """打通指定方向的墙壁"""
        self.walls[direction] = False

    def has_wall(self, direction: str) -> bool:
        return self.walls.get(direction, True)


class Maze:
    """
    迷宫数据结构

    表示:
        grid[y][x] = Cell — 二维网格
        墙壁信息存储在每个 Cell.walls 字典中

    坐标系统:
        (0,0) ────▶ x (东)
         │
         ▼
         y (南)
    """

    def __init__(self, width: int, height: int):
        self.width = width
        self.height = height
        self.grid: List[List[Cell]] = []
        self._init_grid()

    def _init_grid(self):
        """初始化全封闭网格"""
        self.grid = []
        for y in range(self.height):
            row = []
            for x in range(self.width):
                row.append(Cell(x, y))
            self.grid.append(row)

    def get_cell(self, x: int, y: int) -> Optional[Cell]:
        """获取指定坐标的格子，越界返回 None"""
        if 0 <= x < self.width and 0 <= y < self.height:
            return self.grid[y][x]
        return None

    def get_neighbors(self, cell: Cell) -> List[Tuple[Cell, str]]:
        """获取未访问的相邻格子列表: [(相邻格子, 方向), ...]"""
        neighbors = []
        for direction, (dx, dy, _) in DIRECTIONS.items():
            nx, ny = cell.x + dx, cell.y + dy
            neighbor = self.get_cell(nx, ny)
            if neighbor and not neighbor.visited:
                neighbors.append((neighbor, direction))
        return neighbors

    def is_walkable(self, x: int, y: int) -> bool:
        """检查格子是否在迷宫范围内"""
        return 0 <= x < self.width and 0 <= y < self.height

    def is_passable(self, from_x: int, from_y: int, to_x: int, to_y: int) -> bool:
        """检查从 (from_x, from_y) 能否走到 (to_x, to_y)"""
        dx = to_x - from_x
        dy = to_y - from_y

        for direction, (ddx, ddy, _) in DIRECTIONS.items():
            if dx == ddx and dy == ddy:
                cell = self.get_cell(from_x, from_y)
                target = self.get_cell(to_x, to_y)
                if cell and target:
                    return not cell.has_wall(direction)
        return False

    def get_passable_neighbors(self, x: int, y: int) -> List[Tuple[int, int]]:
        """获取可以走到的相邻格子"""
        neighbors = []
        for direction, (dx, dy, _) in DIRECTIONS.items():
            nx, ny = x + dx, y + dy
            if self.is_walkable(nx, ny) and not self.grid[y][x].has_wall(direction):
                neighbors.append((nx, ny))
        return neighbors

    # ── 迷宫生成算法 ─────────────────────────────────

    def generate(self, start_x: int = 0, start_y: int = 0):
        """
        使用递归回溯算法生成迷宫

        时间复杂度: O(width × height)
        空间复杂度: O(width × height) (递归栈)
        """
        self._init_grid()
        stack = []
        current = self.grid[start_y][start_x]
        current.visited = True

        while True:
            neighbors = self.get_neighbors(current)
            if neighbors:
                # 随机选择一个未访问的邻居
                neighbor, direction = random.choice(neighbors)

                # 打通墙壁 (当前格 → 邻居)
                current.remove_wall(direction)
                # 打通墙壁 (邻居 → 当前格)
                opposite = DIRECTIONS[direction][2]
                neighbor.remove_wall(opposite)

                # 进入邻居格子
                neighbor.visited = True
                stack.append(current)
                current = neighbor
            elif stack:
                # 回溯
                current = stack.pop()
            else:
                break

        # 确保起点和终点有开口
        self.grid[0][0].remove_wall("N")                    # 入口
        self.grid[self.height - 1][self.width - 1].remove_wall("S")  # 出口

    # ── 序列化 (供前端渲染) ──────────────────────────

    def to_dict(self) -> dict:
        """将迷宫转换为前端可渲染的字典格式"""
        cells = []
        for y in range(self.height):
            row = []
            for x in range(self.width):
                cell = self.grid[y][x]
                row.append({
                    "x": x,
                    "y": y,
                    "walls": cell.walls.copy(),
                })
            cells.append(row)

        return {
            "width": self.width,
            "height": self.height,
            "cells": cells,
        }

    def to_ascii(self) -> str:
        """生成迷宫的 ASCII 可视化 (调试用)"""
        result = ""
        # 顶部边界
        for x in range(self.width):
            cell = self.grid[0][x]
            result += "+" + ("---" if cell.has_wall("N") else "   ")
        result += "+\n"

        for y in range(self.height):
            # 西墙 + 格子内容
            row_top = ""
            row_mid = ""
            for x in range(self.width):
                cell = self.grid[y][x]
                row_mid += "|" if cell.has_wall("W") else " "
                row_mid += " ● " if (x, y) == (0, 0) else " ★ " if (x, y) == (self.width - 1, self.height - 1) else "   "
            row_mid += "|\n"

            # 南墙
            for x in range(self.width):
                cell = self.grid[y][x]
                row_mid += "+" + ("---" if cell.has_wall("S") else "   ")
            row_mid += "+\n"
            result += row_mid

        return result

    def __repr__(self):
        return f"Maze({self.width}x{self.height})"


# ============================================================
# 自测
# ============================================================
if __name__ == "__main__":
    random.seed(42)
    m = Maze(10, 10)
    m.generate()
    print(m.to_ascii())
    print(f"\n可通行邻居测试 (0,0): {m.get_passable_neighbors(0, 0)}")
    print(f"可通行邻居测试 (9,9): {m.get_passable_neighbors(9, 9)}")
