#!/usr/bin/env python3
"""
Week 2: ROS2 小乌龟速度控制器
==============================
通过发布 /turtle1/cmd_vel 话题来控制 turtlesim 小乌龟的运动。

ROS2 通信模型:
  Publisher (本节点) ──Topic(/turtle1/cmd_vel)──▶ Subscriber (turtlesim_node)

消息类型: geometry_msgs/msg/Twist
  - linear.x:  线速度 x (前进为正)
  - linear.y:  线速度 y (左右平移)
  - angular.z: 角速度 z (逆时针转向为正)

运行方式:
  终端1: ros2 run turtlesim turtlesim_node
  终端2: python3 turtle_controller.py
"""

import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
import math
import time


class TurtleController(Node):
    """小乌龟运动控制器 — 发布速度指令实现预设轨迹"""

    def __init__(self):
        super().__init__('turtle_controller')

        # 创建发布者: 话题名 /turtle1/cmd_vel, 消息类型 Twist, 队列长度 10
        self.publisher = self.create_publisher(Twist, '/turtle1/cmd_vel', 10)

        # 定时器: 每 0.5 秒执行一次 timer_callback
        self.timer = self.create_timer(0.5, self.timer_callback)

        # 状态管理
        self.start_time = time.time()
        self.get_logger().info('🐢 小乌龟控制器已启动')

    def timer_callback(self):
        """
        定时回调 — 根据运行时间切换运动模式
        0-5s:  前进
        5-10s: 逆时针旋转
        10-15s: 前进 + 旋转 (画弧线)
        15-20s: 停止
        """
        elapsed = time.time() - self.start_time
        msg = Twist()

        if elapsed < 5.0:
            # 阶段1: 直线前进
            msg.linear.x = 1.0
            msg.angular.z = 0.0
            self.get_logger().info('⬆️  阶段1: 直线前进')

        elif elapsed < 10.0:
            # 阶段2: 原地旋转
            msg.linear.x = 0.0
            msg.angular.z = 1.0
            self.get_logger().info('🔄 阶段2: 逆时针旋转')

        elif elapsed < 15.0:
            # 阶段3: 前进 + 旋转 = 画弧线
            msg.linear.x = 1.0
            msg.angular.z = 0.5
            self.get_logger().info('↗️  阶段3: 弧线运动')

        else:
            # 阶段4: 停止
            msg.linear.x = 0.0
            msg.angular.z = 0.0
            self.get_logger().info('⏹️  阶段4: 停止')

        self.publisher.publish(msg)


def main(args=None):
    rclpy.init(args=args)
    controller = TurtleController()

    try:
        rclpy.spin(controller)
    except KeyboardInterrupt:
        controller.get_logger().info('🛑 控制器已手动停止')
    finally:
        controller.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
