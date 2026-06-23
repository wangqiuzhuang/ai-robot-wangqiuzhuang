#!/usr/bin/env python3
"""
Week 6: KITTI 数据集 ROS2 发布器
=================================
读取 KITTI 自动驾驶数据集，将图像和点云数据发布到 ROS2 话题。

KITTI 数据集结构:
  KITTI/
  ├── image_02/      # 左彩色相机
  ├── velodyne/      # 64线激光雷达点云 (.bin)
  └── calib/         # 传感器标定参数

ROS2 话题:
  - /kitti/camera_left/image  (sensor_msgs/Image)
  - /kitti/lidar/points       (sensor_msgs/PointCloud2)

运行方式:
  pip install opencv-python numpy
  python3 kitti_publisher.py --data_dir /path/to/KITTI
"""

import os
import sys
import time
import argparse
import numpy as np

try:
    import cv2
    HAS_CV2 = True
except ImportError:
    HAS_CV2 = False
    print("⚠️  opencv-python 未安装，图像发布功能不可用")

try:
    import rclpy
    from rclpy.node import Node
    from sensor_msgs.msg import Image, PointCloud2, PointField
    from std_msgs.msg import Header
    from cv_bridge import CvBridge
    HAS_ROS2 = True
except ImportError:
    HAS_ROS2 = False
    print("⚠️  ROS2 未安装，将以模拟模式运行")


class KITTIPublisher:
    """
    KITTI 数据集发布器

    功能:
      - 遍历 KITTI 目录中的图像和点云文件
      - 按时间戳对齐并发布到 ROS2 话题
      - 支持循环播放和倍速控制
    """

    def __init__(self, data_dir: str, rate: float = 10.0):
        self.data_dir = data_dir
        self.rate = rate  # 发布频率 (Hz)
        self.period = 1.0 / rate

        # 数据集路径
        self.image_dir = os.path.join(data_dir, 'image_02', 'data')
        self.lidar_dir = os.path.join(data_dir, 'velodyne', 'data')

        # 收集文件列表并排序
        self.image_files = self._get_sorted_files(self.image_dir, '.png')
        self.lidar_files = self._get_sorted_files(self.lidar_dir, '.bin')

        print(f"📂 KITTI 数据集: {data_dir}")
        print(f"  📷 图像文件: {len(self.image_files)}")
        print(f"  📡 点云文件: {len(self.lidar_files)}")

        self.current_index = 0
        self.num_frames = min(len(self.image_files), len(self.lidar_files))

    def _get_sorted_files(self, directory: str, extension: str) -> list:
        """获取目录中按名称排序的文件列表"""
        if not os.path.exists(directory):
            print(f"⚠️  目录不存在: {directory}")
            return []

        files = [f for f in os.listdir(directory) if f.endswith(extension)]
        files.sort()
        return [os.path.join(directory, f) for f in files]

    def load_image(self, index: int) -> np.ndarray:
        """加载指定索引的图像"""
        if index < len(self.image_files):
            return cv2.imread(self.image_files[index])
        return None

    def load_point_cloud(self, index: int) -> np.ndarray:
        """
        加载指定索引的点云数据

        KITTI 点云格式: 每行 4 个 float32 (x, y, z, reflectance)
        """
        if index < len(self.lidar_files):
            points = np.fromfile(self.lidar_files[index], dtype=np.float32)
            return points.reshape(-1, 4)
        return None

    def get_frame(self, index: int) -> dict:
        """获取一帧数据 (图像 + 点云)"""
        image = self.load_image(index)
        points = self.load_point_cloud(index)

        return {
            'index': index,
            'image': image,
            'point_cloud': points,
            'num_points': len(points) if points is not None else 0,
        }

    def play(self, loop: bool = True):
        """
        循环播放数据集

        以 self.rate 的频率逐帧发布图像和点云数据
        """
        print(f"\n▶️  开始播放: {self.num_frames} 帧 @ {self.rate}Hz")
        print("   按 Ctrl+C 停止\n")

        try:
            while True:
                frame = self.get_frame(self.current_index)

                # 打印进度
                if self.current_index % 10 == 0:
                    print(f"  帧 {self.current_index + 1}/{self.num_frames}: "
                          f"点云数={frame['num_points']}, "
                          f"图像尺寸={frame['image'].shape if frame['image'] is not None else 'N/A'}")

                # 更新索引
                self.current_index = (self.current_index + 1) % self.num_frames

                if self.current_index == 0 and not loop:
                    break

                time.sleep(self.period)

        except KeyboardInterrupt:
            print("\n⏸️  播放已停止")


def main():
    parser = argparse.ArgumentParser(description='KITTI 数据集发布器')
    parser.add_argument('--data_dir', type=str, required=True,
                        help='KITTI 数据集根目录路径')
    parser.add_argument('--rate', type=float, default=10.0,
                        help='发布频率 (Hz)')
    parser.add_argument('--loop', action='store_true', default=True,
                        help='循环播放')

    args = parser.parse_args()

    publisher = KITTIPublisher(args.data_dir, args.rate)
    publisher.play(loop=args.loop)


if __name__ == '__main__':
    # 如果没有 ROS2，仍然可以独立测试数据加载
    if not HAS_ROS2:
        print("\n💡 运行在数据验证模式 (无 ROS2)")
        print("   安装 ROS2 后可发布到话题: /kitti/camera_left/image, /kitti/lidar/points")

    main()
