#!/usr/bin/env python3
"""
Week 2: 小乌龟位置监听器
==========================
订阅 /turtle1/pose 话题，实时打印小乌龟的位置和姿态信息。

消息类型: turtlesim/msg/Pose
  - x, y: 平面坐标 (float32)
  - theta: 朝向角，弧度 (float32, 0=朝右, π/2=朝上)
  - linear_velocity, angular_velocity: 当前速度

运行方式:
  终端1: ros2 run turtlesim turtlesim_node
  终端2: python3 turtle_pose_listener.py
"""

import rclpy
from rclpy.node import Node
from turtlesim.msg import Pose
import math


class PoseListener(Node):
    """小乌龟位置监听器 — 订阅位姿话题并实时打印"""

    def __init__(self):
        super().__init__('pose_listener')

        # 创建订阅者: 话题 /turtle1/pose, 消息类型 Pose, 回调函数 pose_callback
        self.subscription = self.create_subscription(
            Pose,
            '/turtle1/pose',
            self.pose_callback,
            10  # QoS 队列深度
        )

        self.pose_count = 0
        self.get_logger().info('👂 开始监听小乌龟位置...')

    def pose_callback(self, msg: Pose):
        """每当收到新的位置消息时调用"""
        self.pose_count += 1

        # 将弧度转换为角度（便于阅读）
        theta_deg = math.degrees(msg.theta) % 360

        # 每10次打印一次详细日志（避免刷屏）
        if self.pose_count % 10 == 0:
            self.get_logger().info(
                f'📍 位置 #{self.pose_count}: '
                f'x={msg.x:.3f}, y={msg.y:.3f}, '
                f'θ={theta_deg:.1f}°, '
                f'线速度={msg.linear_velocity:.3f}, '
                f'角速度={msg.angular_velocity:.3f}'
            )


def main(args=None):
    rclpy.init(args=args)
    listener = PoseListener()

    try:
        rclpy.spin(listener)
    except KeyboardInterrupt:
        listener.get_logger().info('🛑 监听已停止')
    finally:
        listener.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
