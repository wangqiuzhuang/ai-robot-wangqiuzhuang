#!/usr/bin/env python3
"""
Week 6: KITTI 点云可视化工具
============================
读取 KITTI 点云 .bin 文件并进行 3D 可视化。

KITTI Velodyne HDL-64E 点云格式:
  - 每点 4 个 float32: (x, y, z, reflectance)
  - x: 向前 (车辆前进方向)
  - y: 向左
  - z: 向上
  - reflectance: 反射强度 (0.0-1.0)

坐标范围:
  - x: [0, 120]m   (前向)
  - y: [-60, 60]m  (左右)
  - z: [-5, 5]m    (高度)

运行方式:
  pip install numpy matplotlib opencv-python
  python3 kitti_visualizer.py /path/to/velodyne/data/000000.bin
"""

import sys
import os
import numpy as np

try:
    import matplotlib.pyplot as plt
    from mpl_toolkits.mplot3d import Axes3D
    HAS_MPL = True
except ImportError:
    HAS_MPL = False


def load_velodyne_bin(filepath: str) -> np.ndarray:
    """加载 KITTI Velodyne 点云 .bin 文件"""
    points = np.fromfile(filepath, dtype=np.float32)
    return points.reshape(-1, 4)


def analyze_point_cloud(points: np.ndarray):
    """分析点云统计特性"""
    x, y, z, r = points[:, 0], points[:, 1], points[:, 2], points[:, 3]

    print(f"\n📊 点云统计分析")
    print(f"{'='*50}")
    print(f"  总点数:     {len(points):,}")
    print(f"  X 范围:     [{x.min():.2f}, {x.max():.2f}] m")
    print(f"  Y 范围:     [{y.min():.2f}, {y.max():.2f}] m")
    print(f"  Z 范围:     [{z.min():.2f}, {z.max():.2f}] m")
    print(f"  反射强度:    [{r.min():.3f}, {r.max():.3f}]")
    print(f"  平均反射率:  {r.mean():.3f}")

    # 距离分析
    distances = np.sqrt(x**2 + y**2 + z**2)
    print(f"  距离范围:    [{distances.min():.2f}, {distances.max():.2f}] m")
    print(f"  平均距离:    {distances.mean():.2f} m")

    # 高度分布
    print(f"\n  高度分布 (Z):")
    for threshold, label in [(0, "地面"), (0.5, "低物体"), (1.5, "中等"), (3.0, "高物体"), (float('inf'), "超高")]:
        count = np.sum(z < threshold) if threshold != float('inf') else len(points)
        print(f"    < {threshold if threshold != float('inf') else '∞'}m: {count:,} 点 ({count/len(points)*100:.1f}%)")


def filter_points(points: np.ndarray,
                  x_range=None, y_range=None, z_range=None,
                  min_distance=None, max_distance=None) -> np.ndarray:
    """按空间范围过滤点云"""
    mask = np.ones(len(points), dtype=bool)

    if x_range:
        mask &= (points[:, 0] >= x_range[0]) & (points[:, 0] <= x_range[1])
    if y_range:
        mask &= (points[:, 1] >= y_range[0]) & (points[:, 1] <= y_range[1])
    if z_range:
        mask &= (points[:, 2] >= z_range[0]) & (points[:, 2] <= z_range[1])

    if min_distance is not None or max_distance is not None:
        dist = np.sqrt(points[:, 0]**2 + points[:, 1]**2 + points[:, 2]**2)
        if min_distance is not None:
            mask &= dist >= min_distance
        if max_distance is not None:
            mask &= dist <= max_distance

    return points[mask]


def visualize_bev(points: np.ndarray, save_path=None):
    """鸟瞰图 (Birds-Eye View) 可视化"""
    if not HAS_MPL:
        print("⚠️  matplotlib 未安装，无法可视化")
        return

    fig, ax = plt.subplots(1, 2, figsize=(14, 6))

    # 左图: XY 投影 (鸟瞰)
    ax[0].scatter(points[:, 0], points[:, 1], c=points[:, 3],
                  s=0.1, cmap='viridis', alpha=0.6)
    ax[0].set_xlabel('X (前向) [m]')
    ax[0].set_ylabel('Y (左向) [m]')
    ax[0].set_title('LiDAR 鸟瞰图 (XY 投影)')
    ax[0].set_aspect('equal')
    ax[0].grid(True, alpha=0.3)
    plt.colorbar(ax[0].collections[0], ax=ax[0], label='反射强度')

    # 右图: XZ 投影 (侧视)
    ax[1].scatter(points[:, 0], points[:, 2], c=points[:, 3],
                  s=0.1, cmap='inferno', alpha=0.6)
    ax[1].set_xlabel('X (前向) [m]')
    ax[1].set_ylabel('Z (高度) [m]')
    ax[1].set_title('LiDAR 侧视图 (XZ 投影)')
    ax[1].grid(True, alpha=0.3)
    plt.colorbar(ax[1].collections[0], ax=ax[1], label='反射强度')

    plt.tight_layout()

    if save_path:
        plt.savefig(save_path, dpi=150)
        print(f"💾 已保存: {save_path}")
    else:
        plt.show()


def main():
    if len(sys.argv) < 2:
        print("用法: python3 kitti_visualizer.py <点云文件.bin> [保存路径]")
        print("示例: python3 kitti_visualizer.py 000000.bin bev_output.png")
        sys.exit(1)

    filepath = sys.argv[1]
    save_path = sys.argv[2] if len(sys.argv) > 2 else None

    if not os.path.exists(filepath):
        print(f"❌ 文件不存在: {filepath}")
        sys.exit(1)

    print(f"📡 加载点云: {filepath}")
    points = load_velodyne_bin(filepath)
    print(f"✅ 加载 {len(points):,} 个点")

    # 统计分析
    analyze_point_cloud(points)

    # 过滤 ROI (感兴趣区域)
    print("\n✂️  过滤 ROI: 前向 0-50m, 横向 ±20m, 高度 -2~3m")
    filtered = filter_points(points,
                             x_range=(0, 50),
                             y_range=(-20, 20),
                             z_range=(-2, 3))
    print(f"   过滤后: {len(filtered):,} 点 (保留 {len(filtered)/len(points)*100:.1f}%)")

    # 可视化
    print("\n📊 生成鸟瞰图...")
    visualize_bev(filtered, save_path)


if __name__ == '__main__':
    main()
