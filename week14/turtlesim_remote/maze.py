#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""turtlesim 迷宫生成模块。

生成一个 COLS×ROWS 的网格迷宫：先用递归回溯得到一棵生成树，再做
"编织"（braid）随机打通一部分墙，制造多条通路与环路——这样最短路径
不再唯一，必须用 BFS / Dijkstra / A* 这类路径搜索算法才能找到最优解。

build_maze() 返回一个 dict：
    obstacles : [{x,y,w,h}]    墙体矩形
    bounds    : {min_x,...}     画布边界
    start/goal: {x,y,...}       起点/终点世界坐标
    grid      : {cols,rows,origin,cell}
    start_cell/goal_cell : (i,j)
    neighbors(cell) -> [cell]   返回与某格连通的相邻格
"""
import random
from collections import deque

ORIGIN = 0.6
COLS = ROWS = 5
CELL = 1.7
WALL_T = 0.3
TURTLE_RADIUS = 0.45
SEED = 7
BRAID = 0.28


def _cell_center(i):
    return ORIGIN + i * CELL + CELL / 2


def _carve(cols, rows, seed):
    rng = random.Random(seed)
    visited = [[False] * cols for _ in range(rows)]
    open_edges = set()
    stack = [(0, 0)]
    visited[0][0] = True
    while stack:
        i, j = stack[-1]
        nbrs = [(i + di, j + dj) for di, dj in ((1, 0), (-1, 0), (0, 1), (0, -1))
                if 0 <= i + di < cols and 0 <= j + dj < rows
                and not visited[j + dj][i + di]]
        if not nbrs:
            stack.pop()
            continue
        ni, nj = rng.choice(nbrs)
        visited[nj][ni] = True
        open_edges.add(frozenset({(i, j), (ni, nj)}))
        stack.append((ni, nj))
    # braid: 随机再打通一些墙，制造环路
    all_edges = []
    for i in range(cols):
        for j in range(rows):
            for di, dj in ((1, 0), (0, 1)):
                ni, nj = i + di, j + dj
                if ni < cols and nj < rows:
                    all_edges.append(frozenset({(i, j), (ni, nj)}))
    for e in all_edges:
        if e not in open_edges and rng.random() < BRAID:
            open_edges.add(e)
    return open_edges


def build_maze(seed=SEED, braid=BRAID, cols=COLS, rows=ROWS):
    global BRAID
    BRAID = braid
    open_edges = _carve(cols, rows, seed)
    obstacles = []
    for i in range(cols - 1):
        for j in range(rows):
            if frozenset({(i, j), (i + 1, j)}) not in open_edges:
                xe = ORIGIN + (i + 1) * CELL
                obstacles.append({"x": round(xe - WALL_T / 2, 3),
                                  "y": round(ORIGIN + j * CELL - WALL_T / 2, 3),
                                  "w": WALL_T, "h": round(CELL + WALL_T, 3)})
    for i in range(cols):
        for j in range(rows - 1):
            if frozenset({(i, j), (i, j + 1)}) not in open_edges:
                ye = ORIGIN + (j + 1) * CELL
                obstacles.append({"x": round(ORIGIN + i * CELL - WALL_T / 2, 3),
                                  "y": round(ye - WALL_T / 2, 3),
                                  "w": round(CELL + WALL_T, 3), "h": WALL_T})

    def neighbors(cell):
        i, j = cell
        out = []
        for di, dj in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            ni, nj = i + di, j + dj
            if 0 <= ni < cols and 0 <= nj < rows and \
               frozenset({(i, j), (ni, nj)}) in open_edges:
                out.append((ni, nj))
        return out

    return {
        "obstacles": obstacles,
        "bounds": {"min_x": ORIGIN, "max_x": ORIGIN + cols * CELL,
                   "min_y": ORIGIN, "max_y": ORIGIN + rows * CELL},
        "start": {"x": _cell_center(0), "y": _cell_center(0), "theta": 0.0},
        "goal": {"x": _cell_center(cols - 1), "y": _cell_center(rows - 1),
                 "radius": 0.55},
        "grid": {"cols": cols, "rows": rows, "origin": ORIGIN, "cell": CELL},
        "start_cell": (0, 0),
        "goal_cell": (cols - 1, rows - 1),
        "open_edges": open_edges,
        "neighbors": neighbors,
        "cell_center": _cell_center,
    }


def _self_check(m):
    """用 BFS 在精细栅格上验证（含半径碰撞）确实可从起点到终点。"""
    obs, b, g = m["obstacles"], m["bounds"], m["goal"]
    r, step = TURTLE_RADIUS, 0.05

    def free(x, y):
        if not (b["min_x"] + r <= x <= b["max_x"] - r
                and b["min_y"] + r <= y <= b["max_y"] - r):
            return False
        for o in obs:
            if o["x"] - r <= x <= o["x"] + o["w"] + r and \
               o["y"] - r <= y <= o["y"] + o["h"] + r:
                return False
        return True

    key = lambda x, y: (round(x / step), round(y / step))
    s = m["start"]
    q = deque([(s["x"], s["y"])])
    seen = {key(s["x"], s["y"])}
    while q:
        x, y = q.popleft()
        if (x - g["x"]) ** 2 + (y - g["y"]) ** 2 <= g["radius"] ** 2:
            return True
        for dx, dy in ((step, 0), (-step, 0), (0, step), (0, -step)):
            nx, ny = round(x + dx, 2), round(y + dy, 2)
            if key(nx, ny) in seen or not free(nx, ny):
                continue
            seen.add(key(nx, ny))
            q.append((nx, ny))
    return False


if __name__ == "__main__":
    m = build_maze()
    n_edges = len(m["open_edges"])
    tree_edges = COLS * ROWS - 1
    print(f"obstacles={len(m['obstacles'])}  open_edges={n_edges} "
          f"(tree={tree_edges}, loops={n_edges - tree_edges})")
    print("BFS solvable:", _self_check(m))
